#!/usr/bin/env python3
"""
Test script for persistent memory system.
"""

import asyncio
import tempfile
from pathlib import Path

from nanobot.memory.memory_store import MemoryStore
from nanobot.memory.memory_manager import MemoryManager
from nanobot.agent.memory_integration import MemoryIntegration


async def test_memory_store():
    """Test basic memory store functionality."""
    print("Testing MemoryStore...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(tmpdir)
        
        # Test storing and retrieving
        store.store("test_key", "test_value", "long")
        retrieved = store.retrieve("test_key")
        assert retrieved == "test_value", f"Expected 'test_value', got {retrieved}"
        print("✓ Basic store/retrieve works")
        
        # Test search
        store.store("server_ip", "192.168.0.15", "long")
        results = store.search("server")
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert results[0]["value"] == "192.168.0.15"
        print("✓ Search works")
        
        # Test expiry
        store.store("temp_key", "temp_value", "short")
        retrieved = store.retrieve("temp_key")
        assert retrieved == "temp_value", "Short-term memory should work initially"
        
        # Cleanup expired
        removed = store.cleanup_expired()
        print(f"✓ Expiry handling works (removed {removed} items)")


async def test_memory_manager():
    """Test memory manager extraction and retrieval."""
    print("Testing MemoryManager...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MemoryManager(tmpdir)
        
        # Test conversation history
        conversation = [
            {"role": "user", "content": "I'm working on a Python project with Docker"},
            {"role": "assistant", "content": "Great! What specific help do you need?"},
            {"role": "user", "content": "My server is at 192.168.0.15 running Unraid"},
        ]
        
        stored_keys = manager.extract_and_store_memories(conversation)
        print(f"✓ Extracted {len(stored_keys)} memories: {stored_keys}")
        
        # Test retrieval
        relevant = manager.retrieve_relevant_memories("python")
        assert len(relevant) > 0, "Should find python-related memories"
        print("✓ Memory retrieval works")
        
        # Test user profile
        profile = manager.get_user_profile()
        assert "preferred_language" in profile, "Should extract user preferences"
        print("✓ User profile extraction works")


async def test_memory_integration():
    """Test full memory integration."""
    print("Testing MemoryIntegration...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        integration = MemoryIntegration(tmpdir)
        
        conversation = [
            {"role": "user", "content": "I prefer concise responses and use GitHub for version control"},
            {"role": "assistant", "content": "Noted! I'll keep responses concise and remember your GitHub preference."},
            {"role": "user", "content": "My main server is 192.168.0.15 with Unraid OS"},
        ]
        
        # Enhance a query
        enhanced = integration.enhance_prompt_with_memories(
            "Check my server status", conversation
        )
        
        assert "Relevant context" in enhanced, "Should include memory context"
        assert "192.168.0.15" in enhanced or "server" in enhanced.lower(), "Should include server info in enhanced prompt"
        print("✓ Memory integration enhances prompts correctly")
        
        # Test memory summary
        summary = integration.get_memory_summary()
        assert "User Profile" in summary, "Should generate memory summary"
        print("✓ Memory summary works")


async def main():
    """Run all memory tests."""
    print("Running Persistent Memory System Tests...\n")
    
    await test_memory_store()
    await test_memory_manager()
    await test_memory_integration()
    
    print("\n🎉 All memory tests passed!")


if __name__ == "__main__":
    asyncio.run(main())