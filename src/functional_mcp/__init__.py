"""
functional-mcp: Turn any MCP server into a Python module

Every MCP server becomes native Python. Automatically.
"""

__version__ = "0.1.0"

from .loader import load_server, load, aload_server, aload
from .registry import register
from .transformation import ArgTransform, transform_tool
from .tools import Tool, ToolCollection, ToolSchema
from .codegen import generate_types_file as generateTypes
from .exceptions import (
    MCPConnectionError,
    MCPToolError,
    MCPResourceError,
    MCPValidationError,
)

__all__ = [
    # Core (primary API)
    "load_server",
    "aload_server",
    
    # Compatibility aliases
    "load",
    "aload",
    
    # Registry
    "register",
    
    # Tools (with metadata)
    "Tool",
    "ToolCollection", 
    "ToolSchema",
    
    # Code generation
    "generateTypes",
    
    # Transformation (enhancement)
    "ArgTransform",
    "transform_tool",
    
    # Exceptions
    "MCPConnectionError",
    "MCPToolError",
    "MCPResourceError",
    "MCPValidationError",
]

