"""
Server wrapper providing functional interface to FastMCP Client.

Lazily loads tools, resources, and prompts on first access.
"""

import asyncio
from typing import Any
from .tools import create_tool, ToolCollection


class ServerWrapper:
    """
    Wrapper around FastMCP Client providing functional interface.
    
    Lazily loads tools/resources/prompts on first access.
    """
    
    def __init__(self, client: Any):
        self._client = client
        self._tools = None
        self._resources = None
        self._prompts = None
    
    @property
    def tools(self) -> ToolCollection:
        """
        Get tools collection (lazy-loaded).
        
        First access lists tools from server and creates ToolCollection.
        Subsequent accesses return cached collection.
        """
        if self._tools is None:
            # List tools from server
            async def _list():
                async with self._client:
                    return await self._client.list_tools()
            
            # Run async
            try:
                loop = asyncio.get_running_loop()
                import nest_asyncio
                nest_asyncio.apply()
                tools_list = loop.run_until_complete(_list())
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    tools_list = loop.run_until_complete(_list())
                finally:
                    loop.close()
            
            # Create Tool objects
            tool_objects = {}
            for tool in tools_list:
                tool_name = self._to_snake_case(tool.name)
                tool_obj = create_tool(
                    name=tool.name,
                    description=getattr(tool, 'description', None),
                    input_schema=getattr(tool, 'inputSchema', {}),
                    client=self._client,
                    meta=getattr(tool, 'meta', {})
                )
                tool_objects[tool_name] = tool_obj
            
            self._tools = ToolCollection(tool_objects)
        
        return self._tools
    
    def __getattr__(self, name: str):
        """
        Proxy attribute access to tools.
        
        server.search(...) delegates to server.tools.search(...)
        """
        if name.startswith("_"):
            raise AttributeError(f"No attribute '{name}'")
        
        # Check if it's a tool
        if self._tools is None:
            # Force tools to load
            self.tools
        
        if name in self._tools._tools:
            return self._tools._tools[name]
        
        raise AttributeError(f"No tool '{name}' available")
    
    def close(self):
        """Close the client connection."""
        # FastMCP Client handles cleanup
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert camelCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


__all__ = ["ServerWrapper"]
