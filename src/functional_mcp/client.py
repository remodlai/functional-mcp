"""
Core MCP client wrapper.

Manages MCP client connection lifecycle and sync/async bridging.
"""

from typing import Any
import asyncio
from fastmcp.client import Client as _MCPClient


class MCPClientWrapper:
    """
    MCP client wrapper for sync/async operations.
    
    Provides both sync and async interfaces to the underlying client.
    """
    
    def __init__(self, client: _MCPClient):
        self.client = client
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop
    
    def run_async(self, coro):
        """Run coroutine synchronously."""
        loop = self._get_loop()
        return loop.run_until_complete(coro)
    
    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call tool synchronously."""
        return self.run_async(self.client.call_tool(name, arguments))
    
    def read_resource(self, uri: str) -> Any:
        """Read resource synchronously."""
        return self.run_async(self.client.read_resource(uri))
    
    def get_prompt(self, name: str, arguments: dict[str, Any]) -> Any:
        """Get prompt synchronously."""
        return self.run_async(self.client.get_prompt(name, arguments))
    
    def list_tools(self) -> Any:
        """List tools synchronously."""
        return self.run_async(self.client.list_tools())
    
    def list_resources(self) -> Any:
        """List resources synchronously."""
        return self.run_async(self.client.list_resources())
    
    def list_prompts(self) -> Any:
        """List prompts synchronously."""
        return self.run_async(self.client.list_prompts())
    
    def initialize(self) -> Any:
        """Initialize connection synchronously."""
        return self.run_async(self.client.initialize())
    
    def close(self):
        """Close client and event loop."""
        if self._loop and not self._loop.is_closed():
            self._loop.close()


__all__ = ["MCPClientWrapper"]
