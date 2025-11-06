"""
Main entry point for loading MCP servers.

Connects to MCP servers and creates dynamic Python modules
with tools as methods, resources as properties, prompts as functions.
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

from .event_loop import AsyncRunner
from .server import create_server_class
from .registry import get_server_command
from .exceptions import MCPConnectionError
from .sampling import create_sampling_handler
from .elicitation import create_elicitation_handler


def load_server(
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
    
    # Create background runner
    runner = AsyncRunner()
    
    # Initialize connection and get server capabilities
    try:
        # Connect and initialize
        async def _init():
            async with client:
                # Context manager auto-initializes
                init_result = client.initialize_result
                
                # List tools
                tools_result = await client.list_tools()
                
                # Try resources (optional)
                try:
                    resources_result = await client.list_resources()
                except:
                    resources_result = []
                
                # Try prompts (optional)
                try:
                    prompts_result = await client.list_prompts()
                except:
                    prompts_result = []
                
                return {
                    "server_info": init_result.serverInfo if init_result else type('obj', (), {"name": "Unknown"})(),
                    "tools": tools_result,
                    "resources": resources_result,
                    "prompts": prompts_result,
                }
        
        # Run using AsyncRunner
        capabilities = runner.run(_init())
        
    except Exception as e:
        runner.close()
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


async def aload_server(
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


def load_server_with_config(
    command: str,
    config: "StdioConfig | str",
) -> Any:
    """
    Load an MCP server with transport configuration.
    
    Use when server requires specific environment variables, working directory,
    or other transport options. Config must match transport type detected from
    command (npx config for npx commands, python config for python commands).
    
    Args:
        command: Server command or registered name. Examples:
            - "npx @org/server" (uses NpxStdioTransport)
            - "python server.py" (uses PythonStdioTransport)
            - "node server.js" (uses StdioTransport)
        
        config: StdioConfig object or saved config name. Config must have
            matching transport_type. Examples:
            - StdioConfig object from create_config().init()
            - "prod" (loads from ~/.config/functional-mcp/configs/prod.json)
    
    Returns:
        Dynamic server object with:
            - .tools: ToolCollection for name-based access
            - Tool methods (e.g., server.search(...))
            - Resources/prompts if server supports them
    
    Raises:
        MCPConnectionError: If connection fails
        FileNotFoundError: If config name doesn't exist
    
    Example:
        # Create and save config
        config = (create_config("prod", transport_type="python")
                 .add_env("API_KEY").with_value(os.getenv("PROD_KEY"))
                 .add_env("DB_HOST").with_value("prod.db.com")
                 .cwd("/app")
                 .init())
        config.save()
        
        # Use saved config
        server = load_server_with_config("python server.py", "prod")
        tools = server.tools
        
    Note:
        MCP servers run in isolated environments. Environment variables from
        your shell are NOT inherited - they must be explicitly passed via config.
        This is an MCP protocol security feature.
    """
    from .config import StdioConfig, load_config as load_stdio_config
    
    # Load config if string
    if isinstance(config, str):
        config = load_stdio_config(config)
    
    # Check registry
    registered = get_server_command(command)
    if registered:
        command = registered
    
    # Create transport with config kwargs
    transport_kwargs = config.to_transport_kwargs()
    
    if command.startswith("npx"):
        parts = command.split()
        package_idx = 1
        while package_idx < len(parts) and parts[package_idx].startswith("-"):
            package_idx += 1
        package = parts[package_idx] if package_idx < len(parts) else ""
        args = parts[package_idx + 1:]
        
        transport = NpxStdioTransport(
            package=package,
            args=args,
            **transport_kwargs
        )
    elif command.startswith("python"):
        parts = command.split()
        script = parts[1] if len(parts) > 1 else command
        
        transport = PythonStdioTransport(
            script_path=script,
            **transport_kwargs
        )
    else:
        # Generic stdio
        parts = command.split()
        cmd = parts[0]
        args = parts[1:]
        
        transport = StdioTransport(
            command=cmd,
            args=args,
            **transport_kwargs
        )
    
    # Create client
    client = Client(transport)
    
    # Use standard load_server flow (without config parameter)
    runner = AsyncRunner()
    
    try:
        async def _init():
            async with client:
                init_result = client.initialize_result
                tools_result = await client.list_tools()
                
                try:
                    resources_result = await client.list_resources()
                except:
                    resources_result = []
                
                try:
                    prompts_result = await client.list_prompts()
                except:
                    prompts_result = []
                
                return {
                    "server_info": init_result.serverInfo if init_result else type('obj', (), {"name": "Unknown"})(),
                    "tools": tools_result,
                    "resources": resources_result,
                    "prompts": prompts_result,
                }
        
        capabilities = runner.run(_init())
        
    except Exception as e:
        runner.close()
        raise MCPConnectionError(f"Connection failed: {e}") from e
    
    # Create server class
    server_class = create_server_class(
        name=capabilities["server_info"].name,
        tools=capabilities["tools"],
        resources=capabilities["resources"],
        prompts=capabilities["prompts"],
        client=client,
        sampling_handler=None,
        elicitation_handler=None,
    )
    
    return server_class()


# Compatibility aliases
load = load_server
aload = aload_server

__all__ = ["load_server", "load_server_with_config", "aload_server", "load", "aload"]
