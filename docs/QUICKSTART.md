# Quick Start Guide

## Installation

```bash
pip install functional-mcp
```

## Basic Usage

```python
from functional_mcp import load_server

# Load any MCP server
server = load_server("npx -y @modelcontextprotocol/server-filesystem /tmp")

# Call tools
files = server.list_directory(path="/tmp")
print(files)

# Close when done
server.close()
```

## Tool Access

### By Name (Clean)

```python
# Get tool collection
tools = server.tools

# Access specific tool
search = tools.search

# Inspect it
print(search.name)
print(search.description)
print(search.schema.required_args)
print(search.schema.optional_args)

# Full schema
schema_dict = search.schema.toDict()

# Call it
result = search(query="test", limit=10)
```

### Direct Call (Shorthand)

```python
# Call directly on server
result = server.search(query="test", limit=10)
```

## Working with Schemas

```python
tool = server.tools.upload_file

# See what it needs
print(f"Required: {tool.schema.required_args}")
print(f"Optional: {tool.schema.optional_args}")

# Build args programmatically
args = {}
for arg in tool.schema.required_args:
    args[arg] = get_value_for(arg)

result = tool(**args)
```

## Tool Transformation

```python
from functional_mcp import ArgTransform, transform_tool

# Get generic tool
forecast = server.tools.get_forecast

# Make it specific
miami = transform_tool(
    forecast,
    name="miami_weather",
    transform_args={
        "lat": ArgTransform(hide=True, default=25.7617),
        "lon": ArgTransform(hide=True, default=-80.1918),
    }
)

# Simpler to use
weather = miami(when="tomorrow")
```

## Server Registry

```python
from functional_mcp import register, load_server

# Register once
register(
    weather="npx weather-server",
    database="python db_server.py"
)

# Load by name anywhere
weather = load_server("weather")
db = load_server("database")
```

## AI Framework Integration

### DSPy

```python
import dspy
from functional_mcp import load_server

tools_server = load_server("tools-server")

agent = dspy.ReAct(
    signature="query -> answer",
    tools=tools_server.tools.toList()  # List of callables
)
```

### Remodl Agents

```python
from remodl.agents import create_agent
from functional_mcp import load_server

tools = load_server("tools-server")

agent = create_agent(
    name="Assistant",
    tools=tools.tools.toList()
)
```

### Anthropic/OpenAI

```python
from anthropic import Anthropic
from functional_mcp import load_server

tools = load_server("tools-server")

client = Anthropic()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=tools.tools.toList(),
    messages=[...]
)
```

## Authentication

### Bearer Token

```python
api = load_server(
    "https://api.example.com/mcp",
    headers={"Authorization": "Bearer sk-1234"}
)
```

### OAuth

```python
# Browser opens automatically
api = load_server("https://api.example.com/mcp", auth="oauth")
```

### Custom

```python
def get_token():
    return my_token_provider()

api = load_server("https://api.example.com/mcp", auth=get_token)
```

## Error Handling

```python
from functional_mcp import MCPToolError

try:
    result = server.process(data="...")
except MCPToolError as e:
    print(f"Tool '{e.tool_name}' failed")
    print(f"Error: {e}")
    print(f"Original: {e.original_error}")
```

## Context Managers

```python
with load_server("service") as server:
    result = server.execute(params="...")
# Auto cleanup
```

## Async

```python
from functional_mcp import aload_server

server = await aload_server("service")
result = await server.process(data="...")
await server.close()
```

## Next Steps

- See [FEATURES.md](FEATURES.md) for complete feature list
- See [EXAMPLES.md](EXAMPLES.md) for real-world examples
- See [API.md](API.md) for API reference

