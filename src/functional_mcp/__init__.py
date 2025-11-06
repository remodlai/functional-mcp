"""
functional-mcp: Turn any MCP server into a Python module

Like mcp2py, but built on FastMCP with tool transformation support.
"""

__version__ = "0.1.0"

from .loader import load, aload
from .registry import register
from .transformation import ArgTransform, transform_tool
from .exceptions import (
    MCPConnectionError,
    MCPToolError,
    MCPResourceError,
    MCPValidationError,
)

__all__ = [
    # Core
    "load",
    "aload",
    
    # Registry
    "register",
    
    # Transformation (enhancement over mcp2py)
    "ArgTransform",
    "transform_tool",
    
    # Exceptions
    "MCPConnectionError",
    "MCPToolError",
    "MCPResourceError",
    "MCPValidationError",
]

