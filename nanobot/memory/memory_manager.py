"""
High-level memory manager that orchestrates memory operations.
"""
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from .memory_store import MemoryStore

class MemoryManager:
    """Manages memory operations with intelligent extraction and retrieval."""
    
    def __init__(self, workspace_path: str = "/root/.nanobot/workspace"):
        self.memory_store = MemoryStore(workspace_path)
        self.workspace_path = workspace_path
        
    def extract_and_store_memories(self, conversation_history: List[Dict[str, str]]) -> List[str]:
        """
        Extract important information from conversation history and store as memories.
        
        Args:
            conversation_history: List of conversation turns with 'role' and 'content'
            
        Returns:
            List of keys for stored memories
        """
        stored_keys = []
        
        # Extract user preferences and settings
        user_preferences = self._extract_user_preferences(conversation_history)
        if user_preferences:
            for key, value in user_preferences.items():
                self.memory_store.store(f"user_preference_{key}", value, "long")
                stored_keys.append(f"user_preference_{key}")
        
        # Extract system information
        system_info = self._extract_system_info(conversation_history)
        if system_info:
            for key, value in system_info.items():
                self.memory_store.store(f"system_{key}", value, "long")
                stored_keys.append(f"system_{key}")
        
        # Extract project context
        project_context = self._extract_project_context(conversation_history)
        if project_context:
            for key, value in project_context.items():
                self.memory_store.store(f"project_{key}", value, "medium")
                stored_keys.append(f"project_{key}")
        
        return stored_keys
    
    def _extract_user_preferences(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract user preferences from conversation."""
        preferences = {}
        full_text = " ".join([turn["content"] for turn in conversation_history])
        
        # Extract technical preferences
        if "python" in full_text.lower():
            preferences["preferred_language"] = "python"
        if "docker" in full_text.lower():
            preferences["container_orchestration"] = "docker"
        if "github" in full_text.lower():
            preferences["version_control"] = "github"
            
        # Extract communication preferences
        if any(word in full_text.lower() for word in ["brief", "concise", "short"]):
            preferences["response_style"] = "concise"
        elif any(word in full_text.lower() for word in ["detailed", "thorough", "comprehensive"]):
            preferences["response_style"] = "detailed"
            
        return preferences
    
    def _extract_system_info(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract system and infrastructure information."""
        system_info = {}
        full_text = " ".join([turn["content"] for turn in conversation_history])
        
        # Extract server info
        if "192.168.0.15" in full_text:
            system_info["main_server"] = "192.168.0.15"
        if "unraid" in full_text.lower():
            system_info["hypervisor"] = "unraid"
        if "docker" in full_text.lower():
            system_info["container_runtime"] = "docker"
            
        # Extract network topology
        if "192.168.0." in full_text:
            # Extract IP ranges mentioned
            ips = re.findall(r"192\.168\.0\.\d+", full_text)
            if ips:
                system_info["known_ips"] = list(set(ips))
                
        return system_info
    
    def _extract_project_context(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract ongoing project context."""
        project_context = {}
        full_text = " ".join([turn["content"] for turn in conversation_history])
        
        # Extract current tasks
        if "memory" in full_text.lower() and "persistent" in full_text.lower():
            project_context["current_task"] = "implement_persistent_memory"
            
        # Extract repository info
        if "github.com/nonewind/nanobot" in full_text:
            project_context["repository"] = "https://github.com/nonewind/nanobot"
            
        return project_context
    
    def retrieve_relevant_memories(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories relevant to the current query.
        
        Args:
            query: Current user query or context
            max_results: Maximum number of memories to return
            
        Returns:
            List of relevant memories with metadata
        """
        # Extract keywords from query for better matching
        import re
        query_words = re.findall(r'\b\w+\b', query.lower())
        
        # Get all memories first
        all_memories = []
        for retention in ["short", "medium", "long"]:
            mem_file = getattr(self.memory_store, f"{retention}_term_file")
            memory_data = self.memory_store._load_memory(mem_file)
            for key, value in memory_data.items():
                # Check expiry
                if value.get("expiry"):
                    from datetime import datetime
                    expiry = datetime.fromisoformat(value["expiry"])
                    if datetime.now() > expiry:
                        continue
                
                all_memories.append({
                    "key": key,
                    "value": value["value"],
                    "source": retention
                })
        
        # Score memories based on keyword matches
        scored_memories = []
        for memory in all_memories:
            combined_text = f"{memory['key']} {str(memory['value'])}".lower()
            score = 0
            
            # Boost score for exact matches
            if query.lower() in combined_text:
                score += 10
            
            # Add score for individual word matches
            for word in query_words:
                if len(word) > 2:  # Ignore very short words
                    score += combined_text.count(word) * 2
            
            # Boost score for system-related memories when query mentions system/server
            if any(term in query.lower() for term in ["server", "system", "status", "check"]):
                if "system_" in memory["key"]:
                    score += 5
            
            if score > 0:
                scored_memories.append((score, memory))
        
        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [mem for score, mem in scored_memories[:max_results]]
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get complete user profile from long-term memories."""
        profile = {}
        
        # Get all user preference memories
        long_term_data = self.memory_store._load_memory(self.memory_store.long_term_file)
        for key, value in long_term_data.items():
            if key.startswith("user_preference_"):
                pref_key = key.replace("user_preference_", "")
                profile[pref_key] = value["value"]
                
        return profile
    
    def get_system_context(self) -> Dict[str, Any]:
        """Get system and infrastructure context."""
        context = {}
        
        long_term_data = self.memory_store._load_memory(self.memory_store.long_term_file)
        for key, value in long_term_data.items():
            if key.startswith("system_"):
                sys_key = key.replace("system_", "")
                context[sys_key] = value["value"]
                
        return context