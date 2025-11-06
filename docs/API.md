# API Reference

## Core Functions

### `load_server(command, **options)`

Load an MCP server and return Python interface.

**Parameters:**
- `command` (str): Server command, URL, or registered name
- `headers` (dict, optional): HTTP headers for remote servers
- `roots` (str | list, optional): Directory roots for filesystem servers
- `on_sampling` (callable, optional): Custom LLM handler
- `on_elicitation` (callable, optional): Custom input handler  
- `allow_sampling` (bool): Allow LLM requests (default: True)
- `allow_elicitation` (bool): Allow user prompts (default: True)
- `auto_auth` (bool): Auto OAuth flow (default: True)
- `timeout` (float): Request timeout in seconds (default: 30.0)

**Returns:** Server object with tools/resources/prompts

**Example:**
```python
server = load_server("npx server-name")
server = load_server("https://api.example.com/mcp")
```

### `aload_server(command, **options)`

Async version of `load_server()`.

**Returns:** Server object with async methods

**Example:**
```python
server = await aload_server("npx server-name")
result = await server.tool(params="...")
```

### `register(**servers)`

Register servers by name.

**Parameters:**
- `**servers`: name=command pairs

**Example:**
```python
register(
    weather="npx weather-server",
    database="python db_server.py"
)
```

### `transform_tool(tool, name=None, description=None, transform_args=None)`

Create transformed version of a tool.

**Parameters:**
- `tool`: Tool object to transform
- `name` (str, optional): New tool name
- `description` (str, optional): New description
- `transform_args` (dict, optional): Argument transformations

**Returns:** Transformed tool

**Example:**
```python
miami = transform_tool(
    forecast,
    name="miami_weather",
    transform_args={
        "lat": ArgTransform(hide=True, default=25.7617)
    }
)
```

## Classes

### `Tool`

First-class tool object with metadata.

**Attributes:**
- `name` (str): Tool name
- `description` (str): Tool description
- `instructions` (str): Alias for description
- `schema` (ToolSchema): Input/output schema

**Methods:**
- `__call__(**kwargs)`: Execute the tool

**Example:**
```python
search = server.tools.search
print(search.name)
result = search(query="test")
```

### `ToolCollection`

Collection of tools with name-based access.

**Methods:**
- `get(name)`: Get tool by name (returns None if not found)
- `list()`: List all tool names
- `toList()`: Get as list of callables (for AI SDKs)
- `__iter__()`: Iterate over tools
- `__getattr__(name)`: Access tool as attribute

**Example:**
```python
tools = server.tools
search = tools.search        # Get by name
all_names = tools.list()     # List names
for tool in tools: ...       # Iterate
```

### `ToolSchema`

Schema information for a tool.

**Attributes:**
- `name` (str): Tool name
- `description` (str | None): Description
- `input_schema` (dict): JSON schema
- `required_args` (list[str]): Required arguments
- `optional_args` (list[str]): Optional arguments

**Methods:**
- `toDict()`: Convert to dictionary
- `to_dict()`: Alias for toDict()

**Example:**
```python
schema = tool.schema
print(schema.required_args)
schema_dict = schema.toDict()
```

### `ArgTransform`

Argument transformation specification.

**Parameters:**
- `name` (str, optional): Rename argument
- `description` (str, optional): New description
- `default` (Any, optional): New default value
- `default_factory` (callable, optional): Generate default (requires hide=True)
- `hide` (bool): Hide from LLM (requires default)
- `required` (bool, optional): Make required
- `type` (type, optional): Change type

**Validation Rules:**
- `hide=True` requires `default` or `default_factory`
- `default_factory` requires `hide=True`
- Cannot use both `default` and `default_factory`

**Example:**
```python
ArgTransform(
    name="search_query",
    description="Natural language search query",
    hide=False
)

ArgTransform(
    hide=True,
    default="Miami"
)
```

## Exceptions

### `MCPConnectionError`

Failed to connect to server.

### `MCPToolError`

Tool execution failed.

**Attributes:**
- `tool_name` (str): Name of failed tool
- `original_error` (Exception | None): Underlying error

### `MCPResourceError`

Resource access failed.

**Attributes:**
- `resource_uri` (str): URI of resource

### `MCPValidationError`

Invalid arguments provided.

**Attributes:**
- `tool_name` (str): Tool name
- `errors` (dict): Validation errors

### `MCPSamplingError`

LLM sampling failed.

### `MCPAuthenticationError`

Authentication failed.

### `MCPElicitationError`

User input elicitation failed.

## Server Object

Dynamically generated object with:

**Tool Methods:**
```python
server.tool_name(params="...")
```

**Tools Collection:**
```python
server.tools  # ToolCollection
server.tools.tool_name  # Tool object
server.tools.list()  # List names
server.tools.toList()  # For AI SDKs
```

**Resources:**
```python
server.STATIC_RESOURCE  # UPPER_CASE
server.dynamic_resource  # lowercase
```

**Prompts:**
```python
server.prompt_name(params="...")
```

**Utility Methods:**
```python
server.close()  # Close connection
```

**Context Manager:**
```python
with server:
    ...
# Auto-closed
```

