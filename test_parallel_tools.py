#!/usr/bin/env python3
"""
Test script for parallel tool execution.
"""

import asyncio
import tempfile
from pathlib import Path

from nanobot.agent.tools.registry import ToolRegistry
from nanobot.agent.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool
from nanobot.agent.tools.web import WebSearchTool, WebFetchTool


async def test_parallel_read_operations():
    """Test that read operations can run in parallel."""
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(ListDirTool())
    
    # Create test files
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        file1 = test_dir / "file1.txt"
        file2 = test_dir / "file2.txt"
        
        file1.write_text("Hello from file 1")
        file2.write_text("Hello from file 2")
        
        # Test parallel execution of read operations
        tool_calls = [
            ("read_file", {"path": str(file1)}),
            ("read_file", {"path": str(file2)}),
            ("list_dir", {"path": str(test_dir)})
        ]
        
        results = await registry.execute_parallel(tool_calls)
        print("Parallel read results:")
        for i, result in enumerate(results):
            print(f"  {i}: {result[:50]}...")
        
        # All should succeed and be fast
        assert "Hello from file 1" in results[0]
        assert "Hello from file 2" in results[1]
        assert "file1.txt" in results[2] and "file2.txt" in results[2]


async def test_mixed_parallel_serial():
    """Test mixed parallel and serial execution."""
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        read_file = test_dir / "readme.txt"
        write_file = test_dir / "output.txt"
        
        read_file.write_text("Original content")
        
        # Mix of parallel-safe and serial-only tools
        tool_calls = [
            ("read_file", {"path": str(read_file)}),      # Can run in parallel
            ("write_file", {"path": str(write_file), "content": "New content"}),  # Must run serially
            ("read_file", {"path": str(read_file)})       # Can run in parallel
        ]
        
        results = await registry.execute_parallel(tool_calls)
        print("Mixed parallel/serial results:")
        for i, result in enumerate(results):
            print(f"  {i}: {result[:50]}...")
        
        assert "Original content" in results[0]
        assert "Successfully wrote" in results[1]
        assert "Original content" in results[2]
        assert write_file.exists()


async def main():
    print("Testing parallel tool execution...")
    await test_parallel_read_operations()
    print("✓ Parallel read operations work")
    
    await test_mixed_parallel_serial()
    print("✓ Mixed parallel/serial execution works")
    
    print("All tests passed! 🎉")


if __name__ == "__main__":
    asyncio.run(main())