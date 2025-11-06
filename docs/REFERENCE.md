# functional-mcp Reference

## Tested & Working (7/7 tests passing)

### Load Server
```python
from functional_mcp import load_server
server = load_server("npx server" | "https://url" | "registered_name")
```

### Tool Access
```python
tools = server.tools                    # ToolCollection
search = tools.search                   # By name
search = tools.get("search")            # Safe get
names = tools.list()                    # All names
for tool in tools: ...                  # Iterate
callables = tools.toList()              # For AI SDKs
```

### Tool Metadata
```python
tool.name                               # str
tool.description                        # str | None
tool.instructions                       # Alias for description
tool.schema.required_args               # list[str]
tool.schema.optional_args               # list[str]
tool.schema.toDict()                    # Complete schema dict
tool.tags                               # list[str] from meta
tool.meta                               # dict[str, Any]
```

### Type Generation
```python
path = tools.generateTypes(
    path='./types/server.py',
    format='pydantic' | 'dataclass' | 'typescript',
    only='input' | 'output' | None,
    with_instructions=True | False
)
```

### ArgTransform Validation
```python
from functional_mcp import ArgTransform

# Valid
ArgTransform(hide=True, default="value")
ArgTransform(name="new_name", description="desc")

# Invalid (raises ValueError)
ArgTransform(hide=True)                                    # Needs default
ArgTransform(default_factory=lambda: "x")                  # Needs hide=True
ArgTransform(default="a", default_factory=lambda: "b")     # Can't have both
```

### Registry
```python
from functional_mcp import register
register(name="command", ...)
```

### Exceptions
```python
MCPConnectionError      # Can't connect
MCPToolError            # Tool failed (has .tool_name, .original_error)
MCPValidationError      # Missing args (has .errors dict)
MCPResourceError        # Resource not found
MCPSamplingError        # LLM failed
MCPAuthenticationError  # Auth failed
MCPElicitationError     # User input failed
```

## Not Yet Implemented

- Full transform_tool() logic (skeleton only)
- Async aload_server() (currently wraps sync)
- Resources implementation
- Prompts implementation
- Integration with real MCP servers (tests skipped)
- Remodl agent helpers

## Implementation Notes

**Serialization:** Uses pydantic_core.to_json() for complex types (dataclasses, Pydantic models, dicts, lists). Primitives (str, int, float, bool) passed unchanged.

**Hydration:** Returns .data if available (hydrated Python objects), else .structured_content, else .content blocks.

**Event Loop:** Sync wrappers create new event loop per call (overhead for high-frequency use - use async for performance).

