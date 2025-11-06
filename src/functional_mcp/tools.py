"""
Tool mapping: MCP tools → Python callable functions.

Handles type conversion, validation, and execution.
"""

from typing import Any, Callable
import inspect


def create_tool_function(
    tool: Any,
    client: Any,
    name: str | None = None,
) -> Callable:
    """
    Create a Python function from an MCP tool definition.
    
    Args:
        tool: MCP tool object
        client: FastMCP client instance
        name: Override function name
    
    Returns:
        Callable Python function with proper signature
    """
    func_name = name or tool.name
    
    # Parse input schema to create function signature
    input_schema = tool.inputSchema or {}
    properties = input_schema.get("properties", {})
    required = set(input_schema.get("required", []))
    
    # Build function
    async def tool_fn(**kwargs) -> dict[str, Any]:
        """Execute MCP tool."""
        # Validate required args
        missing = required - set(kwargs.keys())
        if missing:
            from .exceptions import MCPValidationError
            raise MCPValidationError(
                tool.name,
                f"Missing required arguments: {missing}",
                {"missing": list(missing)}
            )
        
        # Call tool via client
        try:
            result = await client.call_tool(tool.name, kwargs)
            return result.content
        except Exception as e:
            from .exceptions import MCPToolError
            raise MCPToolError(tool.name, str(e), e) from e
    
    # Set metadata
    tool_fn.__name__ = func_name
    tool_fn.__doc__ = tool.description or f"MCP tool: {tool.name}"
    
    # Add type hints (basic version)
    # TODO: Generate full type hints from JSON schema
    
    return tool_fn


def generate_tool_signature(tool: Any) -> inspect.Signature:
    """
    Generate inspect.Signature for a tool from its JSON schema.
    
    Args:
        tool: MCP tool object
    
    Returns:
        Python signature object
    """
    input_schema = tool.inputSchema or {}
    properties = input_schema.get("properties", {})
    required = set(input_schema.get("required", []))
    
    parameters = []
    
    for param_name, param_schema in properties.items():
        # Determine type
        param_type = param_schema.get("type", "string")
        python_type = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }.get(param_type, Any)
        
        # Determine default
        if param_name in required:
            default = inspect.Parameter.empty
        else:
            default = param_schema.get("default", None)
        
        parameters.append(
            inspect.Parameter(
                param_name,
                inspect.Parameter.KEYWORD_ONLY,
                default=default,
                annotation=python_type
            )
        )
    
    return inspect.Signature(parameters, return_annotation=dict[str, Any])


__all__ = ["create_tool_function", "generate_tool_signature"]
