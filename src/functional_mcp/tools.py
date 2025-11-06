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
        meta: Tool metadata (tags, etc.)
    
    Example:
        tools = server.tools
        search = tools.search
        
        print(search.name)         # "search"
        print(search.description)  # "Search for items..."
        print(search.schema.toDict())  # Full schema
        
        # Call with options
        result = search(query="test")
        result = search(query="test", timeout=5.0, meta={"trace_id": "abc"})
    """
    
    def __init__(
        self,
        name: str,
        description: str | None,
        input_schema: dict[str, Any],
        executor: Callable,
        meta: dict[str, Any] | None = None,
    ):
        self.name = name
        self.description = description or f"MCP tool: {name}"
        self.instructions = self.description  # Alias
        self.meta = meta or {}
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
        
        # Extract tags if available
        self.tags = self.meta.get('_fastmcp', {}).get('tags', [])
    
    def __call__(
        self, 
        *,
        timeout: float | None = None,
        progress_handler: Callable | None = None,
        meta: dict[str, Any] | None = None,
        raise_on_error: bool = True,
        **kwargs
    ) -> Any:
        """
        Execute the tool.
        
        Args:
            timeout: Override default timeout for this call
            progress_handler: Callback for progress updates
            meta: Metadata to send (trace_id, source, etc.)
            raise_on_error: Whether to raise on tool errors
            **kwargs: Tool arguments
        
        Returns:
            Hydrated Python object via .data, or content if no schema
        """
        return self._executor(
            **kwargs,
            _timeout=timeout,
            _progress_handler=progress_handler,
            _meta=meta,
            _raise_on_error=raise_on_error
        )
    
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
    
    def generateTypes(
        self,
        path: str,
        format: str = "pydantic",
        only: str | None = None,
        with_instructions: bool = True,
    ) -> str:
        """
        Generate Python type definitions from tool schemas.
        
        Creates typed classes for tool inputs/outputs, enabling
        type-safe tool usage and IDE autocomplete.
        
        Args:
            path: File path to write types (e.g., './types/server_types.py')
            format: Type format ('pydantic', 'dataclass', 'typescript')
            only: Generate only 'input', 'output', or None for both
            with_instructions: Include tool descriptions as docstrings
        
        Returns:
            Path where types were written
        
        Example:
            tools.generateTypes(
                path='./types/weather_types.py',
                format='pydantic',
                only='input',
                with_instructions=True
            )
            
            # Creates:
            # class GetForecastInput(BaseModel):
            #     '''Get weather forecast for a location.'''
            #     lat: float
            #     lon: float
            #     units: str = 'metric'
        """
        from pathlib import Path
        from .codegen import generate_types_file
        
        # Collect all schemas
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "name": tool.name,
                "description": tool.description if with_instructions else None,
                "input_schema": tool.schema.input_schema,
                # TODO: Add output_schema when available
            })
        
        # Generate code
        code = generate_types_file(
            schemas=schemas,
            format=format,
            only=only,
        )
        
        # Write to file
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code)
        
        return str(output_path.absolute())
    
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
    async def executor(
        **kwargs
    ):
        """Execute MCP tool and return hydrated Python objects."""
        # Extract FastMCP-specific parameters (prefixed with _)
        timeout = kwargs.pop('_timeout', None)
        progress_handler = kwargs.pop('_progress_handler', None)
        meta = kwargs.pop('_meta', None)
        raise_on_error = kwargs.pop('_raise_on_error', True)
        
        # Validate required args
        missing = required - set(kwargs.keys())
        if missing:
            from .exceptions import MCPValidationError
            raise MCPValidationError(
                name,
                f"Missing required arguments: {missing}",
                {"missing": list(missing)}
            )
        
        # Call tool with FastMCP options
        try:
            # Build call_tool kwargs
            call_kwargs = {"arguments": kwargs}
            
            if timeout is not None:
                call_kwargs["timeout"] = timeout
            
            if progress_handler is not None:
                call_kwargs["progress_handler"] = progress_handler
            
            if meta is not None:
                call_kwargs["meta"] = meta
            
            # Note: raise_on_error is default in FastMCP, no parameter needed
            result = await client.call_tool(name, **call_kwargs)
            
            # FastMCP's .data property provides:
            # - Fully hydrated Python objects (not just JSON)
            # - Automatic deserialization (datetimes, UUIDs, custom types)
            # - Primitive unwrapping (returns 8 not {"result": 8})
            # - None if no structured output
            
            # Check for errors if raise_on_error=False
            if not raise_on_error and hasattr(result, 'is_error') and result.is_error:
                # Return error info instead of raising
                return {
                    "error": True,
                    "message": result.content[0].text if result.content else "Unknown error"
                }
            
            # Return .data if available (FastMCP feature), else fallback to content
            if hasattr(result, 'data') and result.data is not None:
                return result.data  # Hydrated objects!
            elif hasattr(result, 'structured_content') and result.structured_content is not None:
                return result.structured_content  # Raw JSON
            elif hasattr(result, 'content'):
                # Fallback to content blocks
                if result.content and hasattr(result.content[0], 'text'):
                    return result.content[0].text
                return result.content
            else:
                return result
                
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
