"""Tool registry for dynamic tool management."""

import asyncio
from typing import Any, List, Tuple

from nanobot.agent.tools.base import Tool


class ToolRegistry:
    """
    Registry for agent tools.
    
    Allows dynamic registration and execution of tools.
    """
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
    
    def unregister(self, name: str) -> None:
        """Unregister a tool by name."""
        self._tools.pop(name, None)
    
    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def has(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools
    
    def get_definitions(self) -> list[dict[str, Any]]:
        """Get all tool definitions in OpenAI format."""
        return [tool.to_schema() for tool in self._tools.values()]
    
    async def execute(self, name: str, params: dict[str, Any]) -> str:
        """
        Execute a tool by name with given parameters.
        
        Args:
            name: Tool name.
            params: Tool parameters.
        
        Returns:
            Tool execution result as string.
        
        Raises:
            KeyError: If tool not found.
        """
        tool = self._tools.get(name)
        if not tool:
            return f"Error: Tool '{name}' not found"

        try:
            errors = tool.validate_params(params)
            if errors:
                return f"Error: Invalid parameters for tool '{name}': " + "; ".join(errors)
            return await tool.execute(**params)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"
    
    async def execute_parallel(self, tool_calls: List[Tuple[str, dict[str, Any]]]) -> List[str]:
        """
        Execute multiple tools in parallel if they support parallel execution.
        
        Args:
            tool_calls: List of (tool_name, params) tuples.
        
        Returns:
            List of tool execution results in the same order as input.
        """
        if not tool_calls:
            return []
        
        # Check which tools can run in parallel
        parallel_calls = []
        serial_calls = []
        
        for i, (name, params) in enumerate(tool_calls):
            tool = self._tools.get(name)
            if tool and tool.can_run_in_parallel:
                parallel_calls.append((i, name, params))
            else:
                serial_calls.append((i, name, params))
        
        # Execute parallel calls concurrently
        parallel_results = [None] * len(parallel_calls)
        if parallel_calls:
            async def execute_single(call_info):
                idx, name, params = call_info
                try:
                    tool = self._tools.get(name)
                    if not tool:
                        return f"Error: Tool '{name}' not found"
                    errors = tool.validate_params(params)
                    if errors:
                        return f"Error: Invalid parameters for tool '{name}': " + "; ".join(errors)
                    result = await tool.execute(**params)
                    return result
                except Exception as e:
                    return f"Error executing {name}: {str(e)}"
            
            tasks = [execute_single(call_info) for call_info in parallel_calls]
            parallel_results = await asyncio.gather(*tasks)
        
        # Execute serial calls sequentially
        serial_results = []
        for idx, name, params in serial_calls:
            result = await self.execute(name, params)
            serial_results.append((idx, result))
        
        # Combine results in original order
        final_results = [None] * len(tool_calls)
        
        # Fill parallel results
        for i, (orig_idx, name, params) in enumerate(parallel_calls):
            final_results[orig_idx] = parallel_results[i]
        
        # Fill serial results  
        for orig_idx, result in serial_results:
            final_results[orig_idx] = result
        
        return final_results
    
    @property
    def tool_names(self) -> list[str]:
        """Get list of registered tool names."""
        return list(self._tools.keys())
    
    def __len__(self) -> int:
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        return name in self._tools
