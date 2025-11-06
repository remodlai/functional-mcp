"""
Tool transformation using FastMCP patterns.

This module provides tool transformation capabilities inspired by FastMCP,
allowing you to customize tool schemas and behavior without rewriting tools.
"""

from typing import Any, Callable
from pydantic import BaseModel


class ArgTransform(BaseModel):
    """
    Transformation specification for a tool argument.
    
    Inspired by FastMCP's ArgTransform but adapted for functional-mcp.
    
    Args:
        name: Rename the argument
        description: New description for the argument
        default: New default value
        default_factory: Function to generate default value (requires hide=True)
        hide: Hide argument from LLM (requires default or default_factory)
        required: Make optional argument required
        type: Change the argument type
    
    Example:
        # Rename and improve description
        ArgTransform(
            name="search_query",
            description="The search query in natural language"
        )
        
        # Hide with default
        ArgTransform(
            hide=True,
            default="Miami"
        )
    """
    
    name: str | None = None
    description: str | None = None
    default: Any | None = None
    default_factory: Callable[[], Any] | None = None
    hide: bool = False
    required: bool | None = None
    type: type | None = None
    
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    def model_post_init(self, __context):
        """Validate transformation rules."""
        # Can't use default_factory without hiding
        if self.default_factory and not self.hide:
            raise ValueError("default_factory requires hide=True")
        
        # Can't hide without a default
        if self.hide and self.default is None and self.default_factory is None:
            raise ValueError("hide=True requires default or default_factory")
        
        # Can't have both default and default_factory
        if self.default is not None and self.default_factory is not None:
            raise ValueError("Cannot specify both default and default_factory")


def transform_tool(
    tool: Callable,
    name: str | None = None,
    description: str | None = None,
    transform_args: dict[str, ArgTransform] | None = None,
) -> Callable:
    """
    Create a transformed version of a tool.
    
    Args:
        tool: The tool function to transform
        name: New name for the tool
        description: New description
        transform_args: Dictionary of argument transformations
    
    Returns:
        Transformed tool function
    
    Example:
        from functional_mcp import load, transform_tool, ArgTransform
        
        server = load("weather-server")
        
        # Transform generic forecast to Miami-specific
        miami_weather = transform_tool(
            server.get_forecast,
            name="get_miami_weather",
            description="Get weather forecast for Miami, FL",
            transform_args={
                "lat": ArgTransform(hide=True, default=25.7617),
                "lon": ArgTransform(hide=True, default=-80.1918),
            }
        )
        
        # Simpler interface
        weather = miami_weather(time="tomorrow")
    """
    # TODO: Implement transformation logic
    # For now, return the original tool
    # Full implementation will wrap the tool with transformation logic
    
    return tool


__all__ = ["ArgTransform", "transform_tool"]

