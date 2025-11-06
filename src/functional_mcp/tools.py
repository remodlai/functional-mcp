"""
Tool mapping: MCP tools → Python callable objects with metadata.

Each tool is a first-class object with schema, description, and callable interface.
"""

from typing import Any, Callable
import inspect
from pydantic import BaseModel


class ToolSchema(BaseModel):
    """
    Schema for a tool's inputs and outputs.
    
    Provides clean access to tool metadata.
    """
    
    name: str
    description: str | None = None
    input_schema: dict[str, Any]
    required_args: list[str]
    optional_args: list[str]
    
    def toDict(self) -> dict[str, Any]:
        """Convert schema to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "required": self.required_args,
            "optional": self.optional_args,
        }
    
    def to_dict(self) -> dict[str, Any]:
        """Alias for toDict()."""
        return self.toDict()


class Tool:
    """
    Wrapper for an MCP tool with metadata and callable interface.
    
    Attributes:
        name: Tool name
        description: Tool description
        schema: ToolSchema object
        instructions: Usage instructions (from description)
    
    Example:
        tools = server.tools
        search = tools.search
        
        print(search.name)         # "search"
        print(search.description)  # "Search for items..."
        print(search.schema.toDict())  # Full schema
        
        result = search(query="test")  # Call it
    """
    
    def __init__(
        self,
        name: str,
        description: str | None,
        input_schema: dict[str, Any],
        executor: Callable,
    ):
        self.name = name
        self.description = description or f"MCP tool: {name}"
        self.instructions = self.description  # Alias
        self._executor = executor
        
        # Parse schema
        properties = input_schema.get("properties", {})
        required = set(input_schema.get("required", []))
        
        self.schema = ToolSchema(
            name=name,
            description=description,
            input_schema=input_schema,
            required_args=list(required),
            optional_args=[k for k in properties.keys() if k not in required]
        )
    
    def __call__(self, **kwargs) -> Any:
        """Execute the tool."""
        return self._executor(**kwargs)
    
    def __repr__(self) -> str:
        return f"Tool(name='{self.name}', required={self.schema.required_args})"


class ToolCollection:
    """
    Collection of tools with name-based access.
    
    Allows accessing tools by name as attributes instead of iterating by index.
    
    Example:
        tools = server.tools
        
        # Access by name (not index!)
        search = tools.search
        upload = tools.upload_file
        
        # List all
        for tool in tools:
            print(tool.name)
        
        # Get by name
        tool = tools.get("search")
    """
    
    def __init__(self, tools: dict[str, Tool]):
        self._tools = tools
    
    def __getattr__(self, name: str) -> Tool:
        """Access tool by name."""
        if name.startswith("_"):
            raise AttributeError(f"No attribute '{name}'")
        
        if name in self._tools:
            return self._tools[name]
        
        raise AttributeError(f"No tool named '{name}'. Available: {list(self._tools.keys())}")
    
    def __iter__(self):
        """Iterate over tools."""
        return iter(self._tools.values())
    
    def __len__(self):
        """Number of tools."""
        return len(self._tools)
    
    def get(self, name: str) -> Tool | None:
        """Get tool by name, return None if not found."""
        return self._tools.get(name)
    
    def list(self) -> list[str]:
        """List all tool names."""
        return list(self._tools.keys())
    
    def toList(self) -> list[Callable]:
        """
        Get tools as list of callables for AI SDKs.
        
        For frameworks that expect list of functions (DSPy, LangChain).
        """
        return [tool._executor for tool in self._tools.values()]
    
    def __repr__(self) -> str:
        return f"ToolCollection({len(self._tools)} tools: {self.list()})"


def create_tool(
    name: str,
    description: str | None,
    input_schema: dict[str, Any],
    client: Any,
) -> Tool:
    """
    Create a Tool object from MCP tool definition.
    
    Args:
        name: Tool name
        description: Tool description
        input_schema: JSON schema for inputs
        client: MCP client for execution
    
    Returns:
        Tool object
    """
    properties = input_schema.get("properties", {})
    required = set(input_schema.get("required", []))
    
    # Create executor function
    async def executor(**kwargs) -> dict[str, Any]:
        """Execute MCP tool."""
        # Validate required args
        missing = required - set(kwargs.keys())
        if missing:
            from .exceptions import MCPValidationError
            raise MCPValidationError(
                name,
                f"Missing required arguments: {missing}",
                {"missing": list(missing)}
            )
        
        # Call tool
        try:
            result = await client.call_tool(name, kwargs)
            return result.content
        except Exception as e:
            from .exceptions import MCPToolError
            raise MCPToolError(name, str(e), e) from e
    
    # Make sync wrapper for easier use
    def sync_executor(**kwargs):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(executor(**kwargs))
        finally:
            loop.close()
    
    return Tool(
        name=name,
        description=description,
        input_schema=input_schema,
        executor=sync_executor
    )


__all__ = ["Tool", "ToolCollection", "ToolSchema", "create_tool"]
