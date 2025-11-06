"""
Basic usage examples for functional-mcp.

Demonstrates clean tool access with metadata.
"""

from functional_mcp import load_server, register, ArgTransform, transform_tool


# Example 1: Clean tool access
print("Example 1: Tools with Metadata")
print("=" * 60)

server = load_server("npx -y @modelcontextprotocol/server-filesystem /tmp")

# Access tools collection
tools = server.tools

# Access tool by name (not index!)
list_dir = tools.list_directory

# Get metadata
print(f"Tool name: {list_dir.name}")
print(f"Description: {list_dir.description}")
print(f"Required args: {list_dir.schema.required_args}")
print(f"Optional args: {list_dir.schema.optional_args}")

# Get full schema
schema_dict = list_dir.schema.toDict()
print(f"Schema: {schema_dict}")

# Call it
files = list_dir(path="/tmp")
print(f"Files: {files}")

# Or call directly on server
files2 = server.list_directory(path="/tmp")

server.close()


# Example 2: Iterate over tools
print("\nExample 2: Tool Iteration")
print("=" * 60)

server = load_server("npx tool-server")

# List all tools
print(f"Available tools: {server.tools.list()}")

# Iterate and inspect
for tool in server.tools:
    print(f"\n{tool.name}:")
    print(f"  Description: {tool.description}")
    print(f"  Required: {tool.schema.required_args}")
    print(f"  Optional: {tool.schema.optional_args}")

server.close()


# Example 3: Tool transformation
print("\nExample 3: Tool Transformation")
print("=" * 60)

server = load_server("weather-server")

# Get the generic tool
forecast = server.tools.get_forecast

# Transform it
miami_forecast = transform_tool(
    forecast,
    name="miami_weather",
    transform_args={
        "lat": ArgTransform(hide=True, default=25.7617),
        "lon": ArgTransform(hide=True, default=-80.1918),
    }
)

# Simpler interface
weather = miami_forecast(time="tomorrow")
print(f"Miami weather: {weather}")


# Example 4: Integration with AI frameworks
print("\nExample 4: DSPy Integration")
print("=" * 60)

import dspy
from functional_mcp import load_server

# Load tools
tools_server = load_server("npx tools-server")

# For DSPy (needs list of callables)
dspy_tools = tools_server.tools.toList()

# Use in ReAct
agent = dspy.ReAct(
    signature="query -> answer",
    tools=dspy_tools
)

# Or inspect individual tools first
search = tools_server.tools.search
print(f"Search tool schema: {search.schema.toDict()}")


# Example 5: Server registry
print("\nExample 5: Server Registry")
print("=" * 60)

# Register once
register(
    weather="npx weather-server",
    filesystem="npx filesystem-server /tmp"
)

# Load by name
weather = load_server("weather")
fs = load_server("filesystem")

# Access tools cleanly
get_forecast = weather.tools.get_forecast
print(f"Forecast schema: {get_forecast.schema.toDict()}")


# Example 6: Working with schemas
print("\nExample 6: Schema Introspection")
print("=" * 60)

server = load_server("api-server")

# Get tool
search = server.tools.search

# Examine what it needs
print(f"Tool: {search.name}")
print(f"Required inputs: {search.schema.required_args}")
print(f"Optional inputs: {search.schema.optional_args}")

# Build arguments programmatically
args = {}
for arg in search.schema.required_args:
    args[arg] = input(f"Enter {arg}: ")

# Execute
result = search(**args)
print(f"Result: {result}")
