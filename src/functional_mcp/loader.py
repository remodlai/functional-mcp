"""
Main entry point for loading MCP servers.

Uses FastMCP Client underneath, provides functional interface on top.
"""

import asyncio
from typing import Any, Callable
from fastmcp.client import Client
from fastmcp.client.transports import (
    StdioTransport,
    StreamableHttpTransport,
    PythonStdioTransport,
    NpxStdioTransport,
)

from .server import create_server_class
from .registry import get_server_command
from .exceptions import MCPConnectionError


def load_server(
    command: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float | None = None,
    **kwargs
) -> Any:
    """
    Load an MCP server and return functional interface.
    
    Creates FastMCP Client, verifies connection, returns wrapper.
    Tools/resources/prompts loaded lazily on first access.
    
    Args:
        command: Server command, URL, or registered name
        headers: HTTP headers for remote servers
        timeout: Request timeout in seconds (optional)
        **kwargs: Additional options (reserved)
    
    Returns:
        ServerWrapper with lazy tool/resource/prompt loading
    
    Example:
        server = load_server("http://localhost:4000/mcp",
                            headers={"Authorization": "Bearer sk-1234"})
        # Connected, not yet listed tools
        
        tools = server.tools  # NOW lists tools
    """
    # Check registry
    registered = get_server_command(command)
    if registered:
        command = registered
    
    # Create transport
    if command.startswith(("http://", "https://")):
        transport_kwargs = {"url": command, "headers": headers or {}}
        if timeout is not None:
            transport_kwargs["timeout"] = timeout
        transport = StreamableHttpTransport(**transport_kwargs)
    elif command.startswith("npx"):
        parts = command.split()
        package_idx = 1
        while package_idx < len(parts) and parts[package_idx].startswith("-"):
            package_idx += 1
        package = parts[package_idx] if package_idx < len(parts) else ""
        args = parts[package_idx + 1:]
        transport = NpxStdioTransport(package=package, args=args)
    elif command.startswith("python"):
        transport = PythonStdioTransport(command=command)
    else:
        transport = StdioTransport(command=command)
    
    # Create client
    client = Client(transport)
    
    # Verify connection with ping
    async def _verify():
        async with client:
            result = await client.ping()
            return result
    
    try:
        # Use nest_asyncio for Jupyter compatibility
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio
            nest_asyncio.apply()
            connected = loop.run_until_complete(_verify())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                connected = loop.run_until_complete(_verify())
            finally:
                loop.close()
        
        if not connected:
            raise MCPConnectionError("Server ping failed")
            
    except Exception as e:
        raise MCPConnectionError(f"Connection failed: {e}") from e
    
    # Return wrapper (tools loaded lazily)
    return ServerWrapper(client)


# Alias for compatibility
load = load_server
aload_server = load_server  # TODO: Implement true async version
aload = aload_server

__all__ = ["load_server", "aload_server", "load", "aload"]
