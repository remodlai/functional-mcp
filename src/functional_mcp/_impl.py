"""
Internal implementation module for server loading.

Separated to avoid circular imports between loader and builder.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable
from pathlib import Path

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


def load_server_impl(
    command: str,
    *,
    headers: dict[str, str] | None = None,
    roots: str | list[str] | None = None,
    on_sampling: Callable | None = None,
    on_elicitation: Callable | None = None,
    allow_sampling: bool = False,
    allow_elicitation: bool = False,
    auto_auth: bool = True,
    timeout: float = 30.0,
) -> Any:
    """
    Internal implementation for loading MCP servers.
    
    This is separated into its own module to avoid circular imports
    between loader.py and builder.py.
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
        # Parse npx command: "npx -y @scope/package arg1 arg2"
        parts = command.split()
        npx_flags = []
        package_idx = 1  # Skip "npx"
        
        # Skip npx flags like -y, --yes
        while package_idx < len(parts) and parts[package_idx].startswith("-"):
            npx_flags.append(parts[package_idx])
            package_idx += 1
        
        package = parts[package_idx] if package_idx < len(parts) else ""
        args = parts[package_idx + 1:] if package_idx + 1 < len(parts) else []
        
        transport = NpxStdioTransport(package=package, args=args)
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
    
    # Create dynamic server class
    # Client handles all connection/initialization - we just use it
    server_class = create_server_class(
        client=client,
        sampling_handler=sampling_handler,
        elicitation_handler=elicitation_handler,
    )
    
    return server_class()


__all__ = ["load_server_impl"]

