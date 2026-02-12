"""
Integration of memory system into the main agent loop.
"""
from typing import List, Dict, Any
from ..memory.memory_manager import MemoryManager

class MemoryIntegration:
    """Handles integration of memory system with agent operations."""
    
    def __init__(self, workspace_path: str = "/root/.nanobot/workspace"):
        self.memory_manager = MemoryManager(workspace_path)
        self.workspace_path = workspace_path
        
    def enhance_prompt_with_memories(self, user_query: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Enhance the user query with relevant memories to provide context to LLM.
        
        Args:
            user_query: Current user query
            conversation_history: Full conversation history
            
        Returns:
            Enhanced prompt with memory context
        """
        # Extract and store new memories from recent conversation
        self.memory_manager.extract_and_store_memories(conversation_history)
        
        # Retrieve relevant memories for current query
        relevant_memories = self.memory_manager.retrieve_relevant_memories(user_query)
        
        if not relevant_memories:
            return user_query
            
        # Format memories for LLM context
        memory_context = "Relevant context from previous interactions:\n"
        for memory in relevant_memories:
            memory_context += f"- {memory['key']}: {memory['value']}\n"
        memory_context += "\n"
        
        enhanced_prompt = f"{memory_context}Current query: {user_query}"
        return enhanced_prompt
    
    def get_memory_summary(self) -> str:
        """Get a summary of current memory state for debugging."""
        profile = self.memory_manager.get_user_profile()
        system_ctx = self.memory_manager.get_system_context()
        
        summary = "Memory Summary:\n"
        summary += f"User Profile: {profile}\n"
        summary += f"System Context: {system_ctx}\n"
        
        # Count memories
        short_count = len(self.memory_manager.memory_store._load_memory(
            self.memory_manager.memory_store.short_term_file))
        medium_count = len(self.memory_manager.memory_store._load_memory(
            self.memory_manager.memory_store.medium_term_file))
        long_count = len(self.memory_manager.memory_store._load_memory(
            self.memory_manager.memory_store.long_term_file))
            
        summary += f"Memory counts - Short: {short_count}, Medium: {medium_count}, Long: {long_count}"
        
        return summary