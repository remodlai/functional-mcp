# functional-mcp

Turn any MCP server into a Python module using FastMCP.

Like mcp2py, but built on FastMCP with tool transformation support.

## Quick Start

```python
from functional_mcp import load

# Load MCP server
server = load("npx -y @modelcontextprotocol/server-filesystem /tmp")

# Tools become Python methods
files = server.list_directory(path="/tmp")
content = server.read_file(path="/tmp/test.txt")
```

## Key Features

- **Tool Transformation**: Rename, remap, and customize tools using FastMCP's ArgTransform
- **Auto-completion**: IDE autocomplete for all tools
- **Type Safety**: Full type hints generated from schemas
- **FastMCP Powered**: Built on FastMCP for better docs and ecosystem consistency

## Installation

```bash
pip install functional-mcp
```

## Tool Transformation

```python
from functional_mcp import load, transform_tool
from functional_mcp import ArgTransform

server = load("weather-server")

# Transform a generic tool to be Miami-specific
miami_weather = transform_tool(
    server.get_forecast,
    name="get_miami_weather",
    transform_args={
        "lat": ArgTransform(hide=True, default=25.7617),
        "lon": ArgTransform(hide=True, default=-80.1918),
    }
)

# Now simpler to use
weather = miami_weather(time="tomorrow")
```

## Integration with Remodl SDK

```python
from functional_mcp import load
import remodl

# Load MCP tools
server = load("npx filesystem-server /tmp")

# Use with Remodl agents
from remodl.agents import create_agent

agent = create_agent(
    name="File Assistant",
    tools=server.tools  # Auto-compatible!
)
```

## Advantages over mcp2py

1. **Better Documentation** - FastMCP has comprehensive docs
2. **Tool Transformation** - Customize tools without forking
3. **Ecosystem Consistency** - Same patterns as FastAPI/Pydantic
4. **Remodl Integration** - Built for Remodl SDK from the ground up

