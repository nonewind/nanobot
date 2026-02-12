"""
Memory storage implementation with different retention policies.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

class MemoryStore:
    """Base memory store with different retention levels."""
    
    def __init__(self, workspace_path: str = "/root/.nanobot/workspace"):
        self.workspace_path = Path(workspace_path)
        self.memory_dir = self.workspace_path / "memory"
        self.memory_dir.mkdir(exist_ok=True)
        
        # Memory files for different retention levels
        self.short_term_file = self.memory_dir / "short_term.json"
        self.medium_term_file = self.memory_dir / "medium_term.json" 
        self.long_term_file = self.memory_dir / "long_term.json"
        
        # Initialize memory files if they don't exist
        for mem_file in [self.short_term_file, self.medium_term_file, self.long_term_file]:
            if not mem_file.exists():
                mem_file.write_text(json.dumps({}))
    
    def _load_memory(self, memory_file: Path) -> Dict[str, Any]:
        """Load memory from file."""
        try:
            return json.loads(memory_file.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_memory(self, memory_file: Path, data: Dict[str, Any]) -> None:
        """Save memory to file."""
        memory_file.write_text(json.dumps(data, indent=2, default=str))
    
    def store(self, key: str, value: Any, retention: str = "medium") -> bool:
        """
        Store a memory with specified retention level.
        
        Args:
            key: Memory key/identifier
            value: Memory value (will be JSON serialized)
            retention: "short", "medium", or "long"
        """
        if retention == "short":
            memory_file = self.short_term_file
            # Short-term: expires in 1 hour
            expiry = datetime.now() + timedelta(hours=1)
            value = {"value": value, "expiry": expiry.isoformat()}
        elif retention == "medium":
            memory_file = self.medium_term_file
            # Medium-term: expires in 30 days
            expiry = datetime.now() + timedelta(days=30)
            value = {"value": value, "expiry": expiry.isoformat()}
        else:  # long-term
            memory_file = self.long_term_file
            # Long-term: no expiry
            value = {"value": value, "expiry": None}
        
        memory_data = self._load_memory(memory_file)
        memory_data[key] = value
        self._save_memory(memory_file, memory_data)
        return True
    
    def retrieve(self, key: str, retention: str = "all") -> Optional[Any]:
        """
        Retrieve a memory by key.
        
        Args:
            key: Memory key to retrieve
            retention: "short", "medium", "long", or "all"
        """
        files_to_check = []
        if retention == "all":
            files_to_check = [self.short_term_file, self.medium_term_file, self.long_term_file]
        elif retention == "short":
            files_to_check = [self.short_term_file]
        elif retention == "medium":
            files_to_check = [self.medium_term_file]
        else:  # long
            files_to_check = [self.long_term_file]
        
        for mem_file in files_to_check:
            memory_data = self._load_memory(mem_file)
            if key in memory_data:
                stored_value = memory_data[key]
                # Check expiry for short and medium term
                if stored_value.get("expiry"):
                    expiry = datetime.fromisoformat(stored_value["expiry"])
                    if datetime.now() > expiry:
                        # Expired, remove it
                        del memory_data[key]
                        self._save_memory(mem_file, memory_data)
                        continue
                
                return stored_value["value"]
        
        return None
    
    def search(self, query: str, retention: str = "all") -> List[Dict[str, Any]]:
        """
        Search memories by query string.
        """
        results = []
        files_to_check = []
        
        if retention == "all":
            files_to_check = [self.short_term_file, self.medium_term_file, self.long_term_file]
        elif retention == "short":
            files_to_check = [self.short_term_file]
        elif retention == "medium":
            files_to_check = [self.medium_term_file]
        else:  # long
            files_to_check = [self.long_term_file]
        
        for mem_file in files_to_check:
            memory_data = self._load_memory(mem_file)
            for key, value in memory_data.items():
                # Check expiry
                if value.get("expiry"):
                    expiry = datetime.fromisoformat(value["expiry"])
                    if datetime.now() > expiry:
                        continue
                
                # Search in key and value
                searchable_content = f"{key} {str(value['value'])}".lower()
                if query.lower() in searchable_content:
                    results.append({
                        "key": key,
                        "value": value["value"],
                        "source": mem_file.name.replace(".json", "")
                    })
        
        return results
    
    def cleanup_expired(self) -> int:
        """Clean up expired memories and return count of removed items."""
        removed_count = 0
        
        for mem_file in [self.short_term_file, self.medium_term_file]:
            memory_data = self._load_memory(mem_file)
            original_count = len(memory_data)
            
            # Filter out expired items
            cleaned_data = {}
            for key, value in memory_data.items():
                if value.get("expiry"):
                    expiry = datetime.fromisoformat(value["expiry"])
                    if datetime.now() <= expiry:
                        cleaned_data[key] = value
                else:
                    cleaned_data[key] = value
            
            removed_count += original_count - len(cleaned_data)
            if original_count != len(cleaned_data):
                self._save_memory(mem_file, cleaned_data)
        
        return removed_count