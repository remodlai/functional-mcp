"""
Server registry for storing commonly-used MCP servers.

Allows registering servers by name for easy loading.
"""

import json
import os
from pathlib import Path


_REGISTRY_PATH = Path.home() / ".config" / "functional-mcp" / "servers.json"
_registry: dict[str, str] = {}


def register(**servers: str) -> None:
    """
    Register MCP servers by name.
    
    Args:
        **servers: Mapping of names to server commands/URLs
    
    Example:
        ```python
        from functional_mcp import register, load
        
        # Register once
        register(
            weather="npx -y @h1deya/mcp-server-weather",
            filesystem="npx -y @modelcontextprotocol/server-filesystem /tmp"
        )
        
        # Load by name anywhere
        weather = load("weather")
        fs = load("filesystem")
        ```
    """
    global _registry
    
    # Load existing registry
    if _REGISTRY_PATH.exists():
        with open(_REGISTRY_PATH) as f:
            _registry = json.load(f)
    
    # Update with new servers
    _registry.update(servers)
    
    # Save to disk
    _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_REGISTRY_PATH, 'w') as f:
        json.dump(_registry, f, indent=2)


def get_server_command(name: str) -> str | None:
    """
    Get server command by name.
    
    Args:
        name: Server name
    
    Returns:
        Server command/URL or None if not found
    """
    global _registry
    
    # Load registry if empty
    if not _registry and _REGISTRY_PATH.exists():
        with open(_REGISTRY_PATH) as f:
            _registry = json.load(f)
    
    return _registry.get(name)


def list_servers() -> dict[str, str]:
    """
    List all registered servers.
    
    Returns:
        Dictionary of server names to commands
    """
    global _registry
    
    if not _registry and _REGISTRY_PATH.exists():
        with open(_REGISTRY_PATH) as f:
            _registry = json.load(f)
    
    return _registry.copy()


__all__ = ["register", "get_server_command", "list_servers"]

