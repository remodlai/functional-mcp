"""
Main entry point for loading MCP servers.

Uses FastMCP Client to connect to MCP servers and creates
dynamic Python modules with tools as methods.
"""

import asyncio
from pathlib import Path
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
from .sampling import create_sampling_handler
from .elicitation import create_elicitation_handler


def load(
    command: str,
    *,
    headers: dict[str, str] | None = None,
    roots: str | list[str] | None = None,
    on_sampling: Callable | None = None,
    on_elicitation: Callable | None = None,
    allow_sampling: bool = True,
    allow_elicitation: bool = True,
    auto_auth: bool = True,
    timeout: float = 30.0,
) -> Any:
    """
    Load an MCP server and return it as a Python module.
    
    Detects transport type automatically:
    - URLs (http://, https://) → HTTP/SSE transport
    - Commands starting with "npx" → Node stdio transport
    - Commands starting with "python" → Python stdio transport
    - Other commands → Generic stdio transport
    
    Args:
        command: Server command/URL or registered name
        headers: HTTP headers for remote servers
        roots: Directory roots for filesystem servers
        on_sampling: Custom LLM sampling handler (uses Remodl if None)
        on_elicitation: Custom user input handler (uses terminal if None)
        allow_sampling: Whether to allow LLM sampling
        allow_elicitation: Whether to allow user input
        auto_auth: Auto-handle OAuth
        timeout: Request timeout
    
    Returns:
        Dynamic server object with tools as methods
    """
    # Check registry first
    registered_command = get_server_command(command)
    if registered_command:
        command = registered_command
    
    # Detect transport type
    if command.startswith(("http://", "https://")):
        transport = StreamableHttpTransport(
            url=command,
            headers=headers or {},
            timeout=timeout
        )
    elif command.startswith("npx"):
        transport = NpxStdioTransport(command=command)
    elif command.startswith("python"):
        transport = PythonStdioTransport(command=command)
    else:
        transport = StdioTransport(command=command)
    
    # Create client
    client = Client(transport)
    
    # Setup sampling handler
    if allow_sampling:
        sampling_handler = on_sampling or create_sampling_handler()
    else:
        sampling_handler = None
    
    # Setup elicitation handler
    if allow_elicitation:
        elicitation_handler = on_elicitation or create_elicitation_handler()
    else:
        elicitation_handler = None
    
    # Initialize connection and get server capabilities
    try:
        # Connect and initialize
        async def _init():
            async with client:
                # Initialize server
                init_result = await client.initialize()
                
                # List tools, resources, prompts
                tools_result = await client.list_tools()
                resources_result = await client.list_resources()
                prompts_result = await client.list_prompts()
                
                return {
                    "server_info": init_result.server_info,
                    "tools": tools_result.tools,
                    "resources": resources_result.resources if resources_result else [],
                    "prompts": prompts_result.prompts if prompts_result else [],
                }
        
        # Run async initialization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        capabilities = loop.run_until_complete(_init())
        
    except Exception as e:
        raise MCPConnectionError(f"Failed to connect to server: {e}") from e
    
    # Create dynamic server class
    server_class = create_server_class(
        name=capabilities["server_info"].name,
        tools=capabilities["tools"],
        resources=capabilities["resources"],
        prompts=capabilities["prompts"],
        client=client,
        sampling_handler=sampling_handler,
        elicitation_handler=elicitation_handler,
    )
    
    # Instantiate and return
    return server_class()


async def aload(
    command: str,
    **kwargs: Any,
) -> Any:
    """
    Async version of load().
    
    All tools become async methods that must be awaited.
    
    Args:
        command: Server command/URL or registered name
        **kwargs: Same options as load()
    
    Returns:
        Dynamic server object with async methods
    
    Example:
        >>> server = await aload("npx -y server-filesystem /tmp")
        >>> files = await server.list_directory(path="/tmp")
        >>> await server.close()
    """
    # TODO: Implement fully async version
    # For now, use sync version
    return load(command, **kwargs)


__all__ = ["load", "aload"]
