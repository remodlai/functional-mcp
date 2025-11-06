"""
Example: Clean tool access with full metadata.

Shows the improved tool interface vs mcp2py.
"""

from functional_mcp import load_server


# Load a server
server = load_server("npx -y @modelcontextprotocol/server-filesystem /tmp")

print("Clean Tool Access Pattern")
print("=" * 60)

# Access tools collection
tools = server.tools

# Get tool by name (NOT by index!)
list_dir = tools.list_directory

print(f"Tool Name: {list_dir.name}")
print(f"Description: {list_dir.description}")
print(f"Instructions: {list_dir.instructions}")  # Alias for description

# Get schema details
print(f"\nRequired Arguments: {list_dir.schema.required_args}")
print(f"Optional Arguments: {list_dir.schema.optional_args}")

# Full schema as dict
schema_dict = list_dir.schema.toDict()
print(f"\nFull Schema:")
for key, value in schema_dict.items():
    print(f"  {key}: {value}")

# Call the tool
result = list_dir(path="/tmp")
print(f"\nResult: {result}")

# Or use shorthand
result2 = server.list_directory(path="/tmp")

print("\n" + "=" * 60)
print("List All Tools")
print("=" * 60)

# List names
print(f"Available: {tools.list()}")

# Iterate over all
for tool in tools:
    print(f"\n{tool.name}:")
    print(f"  {tool.description}")
    print(f"  Required: {tool.schema.required_args}")

# Get specific tool
search_tool = tools.get("search_files")
if search_tool:
    print(f"\nFound search_files tool")
    print(f"Schema: {search_tool.schema.toDict()}")

server.close()


# Compare with mcp2py pattern (old way)
print("\n" + "=" * 60)
print("Comparison: mcp2py vs functional-mcp")
print("=" * 60)

print("""
mcp2py (annoying):
    tools = server.tools  # Just a list
    tools[0].__name__     # Access by index
    tools[1].__name__     # Have to know index
    # No clean way to get tool by name
    # No schema access

functional-mcp (clean):
    tools = server.tools           # ToolCollection
    search = tools.search          # Access by name!
    print(search.name)             # Metadata
    print(search.description)      # Clear
    print(search.schema.toDict())  # Full schema
    result = search(query="test")  # Call it
""")

