"""
Exceptions for functional-mcp.

Matches mcp2py exception hierarchy for compatibility.
"""


class MCPError(Exception):
    """Base exception for all MCP-related errors."""
    pass


class MCPConnectionError(MCPError):
    """Failed to connect to MCP server."""
    pass


class MCPToolError(MCPError):
    """Tool execution failed."""
    
    def __init__(self, tool_name: str, message: str, original_error: Exception | None = None):
        self.tool_name = tool_name
        self.original_error = original_error
        super().__init__(f"Tool '{tool_name}' failed: {message}")


class MCPResourceError(MCPError):
    """Resource not found or access failed."""
    
    def __init__(self, resource_uri: str, message: str):
        self.resource_uri = resource_uri
        super().__init__(f"Resource '{resource_uri}' error: {message}")


class MCPValidationError(MCPError):
    """Invalid arguments provided to tool."""
    
    def __init__(self, tool_name: str, message: str, errors: dict | None = None):
        self.tool_name = tool_name
        self.errors = errors or {}
        super().__init__(f"Validation error for '{tool_name}': {message}")


class MCPSamplingError(MCPError):
    """LLM sampling failed or not configured."""
    pass


class MCPAuthenticationError(MCPError):
    """Authentication failed."""
    pass


class MCPElicitationError(MCPError):
    """User input elicitation failed."""
    pass

