"""
Basic usage examples for functional-mcp.

Demonstrates core features with mcp2py API compatibility.
"""

from functional_mcp import load, register, ArgTransform, transform_tool


# Example 1: Basic tool calling
print("Example 1: Basic Usage")
print("=" * 60)

server = load("npx -y @modelcontextprotocol/server-filesystem /tmp")

# Tools become Python methods
files = server.list_directory(path="/tmp")
print(f"Files in /tmp: {files}")

server.close()


# Example 2: Server registry
print("\nExample 2: Server Registry")
print("=" * 60)

# Register commonly-used servers
register(
    weather="npx -y @h1deya/mcp-server-weather",
    filesystem="npx -y @modelcontextprotocol/server-filesystem /tmp"
)

# Load by name
weather = load("weather")
print(f"Weather server loaded: {weather}")
weather.close()


# Example 3: Tool transformation (FastMCP enhancement!)
print("\nExample 3: Tool Transformation")
print("=" * 60)

server = load("weather-server")

# Transform generic tool to Miami-specific
miami_weather = transform_tool(
    server.get_forecast,
    name="get_miami_weather",
    description="Get weather forecast for Miami, FL",
    transform_args={
        "lat": ArgTransform(hide=True, default=25.7617),
        "lon": ArgTransform(hide=True, default=-80.1918),
        "units": ArgTransform(hide=True, default="imperial"),
    }
)

# Now much simpler to use
weather = miami_weather(time="tomorrow")
print(f"Miami weather: {weather}")


# Example 4: Integration with Remodl agents
print("\nExample 4: Remodl Integration")
print("=" * 60)

from remodl.agents import create_agent

# Load MCP tools
fs_server = load("filesystem")

# Create agent with MCP tools
agent = create_agent(
    name="File Assistant",
    role="You help users manage their files",
    tools=fs_server.tools  # Auto-compatible!
)

# Agent can now use MCP tools
result = agent.execute(query="List files in /tmp")
print(f"Agent result: {result}")


# Example 5: Context manager
print("\nExample 5: Context Manager")
print("=" * 60)

with load("npx test-server") as server:
    result = server.echo(message="Hello!")
    print(f"Echo result: {result}")
# Server automatically closed


# Example 6: HTTP server with auth
print("\nExample 6: Remote Server with Auth")
print("=" * 60)

api = load(
    "https://api.example.com/mcp",
    headers={"Authorization": "Bearer sk-1234567890"}
)

result = api.search(query="test")
print(f"API result: {result}")
api.close()

