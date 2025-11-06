# Features

## ToolCollection: Name-Based Access

**Problem:** mcp2py forces index iteration
```python
# mcp2py
tools = server.tools  # list
tools[0].__name__  # "search"
tools[1].__name__  # "upload"
# No dict, no get(), have to iterate to find by name
```

**Solution:** ToolCollection with attribute access
```python
# functional-mcp
tools = server.tools  # ToolCollection
search = tools.search  # Direct access
upload = tools.get("upload_file")  # Or use get()
```

**When to use:**
- Building UIs that need specific tools
- Agent systems selecting tools by name
- Dynamic tool loading based on requirements

## Tool Metadata Exposure

Each `Tool` object exposes full metadata:

```python
tool = server.tools.search

tool.name          # "search"
tool.description   # Full description
tool.instructions  # Alias for description
tool.schema        # ToolSchema object

# Schema details
tool.schema.required_args  # ["query"]
tool.schema.optional_args  # ["limit", "category"]
tool.schema.toDict()       # Full JSON schema
```

**Why this matters:**
- Validate compatibility before assigning to agent
- Build dynamic UIs from schemas
- Generate documentation programmatically
- Query requirements in semantic DSL

## Hydrated Python Objects

Returns typed objects, not JSON strings:

```python
weather = server.get_weather(city="NYC")

# You get Python objects:
weather.timestamp    # datetime(2024, 1, 15, 14, 30)
weather.station_id   # UUID('123e4567-...')
weather.forecast     # WeatherForecast(temp=20, ...)

# Not string parsing:
datetime.fromisoformat(weather["timestamp"])  # ← Don't need this
```

**Implementation:** Uses FastMCP's `.data` property which deserializes based on output schema.

**Fallback:** If no schema or deserialization fails, returns content blocks.

**When it fails:** Legacy servers without output schemas return `None` for .data.

## Primitive Unwrapping

Servers wrap primitives: `{"result": 8}`

functional-mcp unwraps automatically:

```python
sum_value = server.calculate(a=5, b=3)
# Returns: 8 (not {"result": 8})

# Compare with raw MCP:
result = call_tool_raw("calculate", {"a": 5, "b": 3})
value = result["result"]  # Manual unwrapping
```

**Why:** Cleaner code, matches Python conventions, reduces boilerplate.

## Tool Transformation

Customize tools without modifying server:

```python
from functional_mcp import ArgTransform, transform_tool

# Problem: Generic tool has too many params for agent
forecast = server.get_forecast
# forecast(lat, lon, units, locale, detail_level, ...)

# Solution: Hide irrelevant params
miami_weather = transform_tool(
    forecast,
    transform_args={
        "lat": ArgTransform(hide=True, default=25.7617),
        "lon": ArgTransform(hide=True, default=-80.1918),
        "units": ArgTransform(hide=True, default="imperial"),
    }
)

# Agent sees simple interface
miami_weather(when="tomorrow")  # One param!
```

**Use cases:**
- Simplify tools for LLM agents (fewer params = better tool use)
- Create domain-specific variants (miami_weather, tokyo_weather)
- Hide infrastructure params (debug flags, internal IDs)
- Set organizational defaults (always use company DB connection)

**Validation:**
- `hide=True` requires `default` or `default_factory`
- `default_factory` requires `hide=True`
- Can't use both `default` and `default_factory`

## Remodl SDK Integration

Sampling uses Remodl instead of litellm:

**Priority:** REMODL_API_KEY → ANTHROPIC_API_KEY → OPENAI_API_KEY → GOOGLE_API_KEY

**Why:** Automatic integration with Remodl infrastructure, uses your proxy, leverages Nova models, consistent ecosystem.

**Override:**
```python
server = load_server("server", on_sampling=custom_handler)
```

## Server Registry

Persist server configurations:

```python
from functional_mcp import register

register(
    prod_db="python prod_db_server.py",
    staging_db="python staging_db_server.py"
)

# Load by environment
db = load_server("prod_db" if is_production else "staging_db")
```

**Storage:** `~/.config/functional-mcp/servers.json`

**Team usage:** Check registry file into git for shared configs.

## Type Generation

Auto-generates `.pyi` stubs for IDE support:

**Location:** `~/.cache/functional-mcp/stubs/<command_hash>.pyi`

**Content:**
```python
class WeatherServer:
    def get_forecast(self, lat: float, lon: float) -> dict[str, Any]: ...
    def get_alerts(self, state: str) -> dict[str, Any]: ...
```

**Manual generation:**
```python
server.generate_stubs("./stubs/weather.pyi")
```

**When to use:** 
- Committing stubs to repo for team
- Generating docs from stubs
- Type checking in CI

## Authentication

### OAuth (PKCE)

Browser opens automatically, tokens cached:

```python
api = load_server("https://api.com/mcp", auth="oauth")
# 1. Browser opens
# 2. You log in
# 3. Token saved to ~/.config/functional-mcp/tokens.json
# 4. Auto-refreshed on expiry
```

**Disable for CI:**
```python
api = load_server("https://api.com/mcp", auto_auth=False)
```

### Bearer Token

```python
api = load_server("https://api.com/mcp",
                 headers={"Authorization": "Bearer sk-..."})
```

### Custom Auth

```python
def get_token():
    return fetch_from_vault()

api = load_server("https://api.com/mcp", auth=get_token)
```

## Error Handling

Specific exceptions with context:

```python
from functional_mcp import MCPToolError, MCPValidationError

try:
    result = server.process(data="...")
except MCPValidationError as e:
    # Missing required args
    print(f"Missing: {e.errors['missing']}")
except MCPToolError as e:
    # Tool execution failed
    print(f"Tool {e.tool_name} failed")
    print(f"Original: {e.original_error}")
```

**Exception hierarchy:**
```
MCPError
├── MCPConnectionError (can't connect)
├── MCPToolError (tool failed)
├── MCPResourceError (resource not found)
├── MCPValidationError (invalid args)
├── MCPSamplingError (LLM request failed)
├── MCPAuthenticationError (auth failed)
└── MCPElicitationError (user input failed)
```

## Async Support

```python
from functional_mcp import aload_server

server = await aload_server("server")
result = await server.tool(params="...")

# Concurrent
results = await asyncio.gather(
    server.tool_1(),
    server.tool_2()
)
```

**When to use:** High-throughput scenarios, concurrent tool calls, async frameworks.

## Context Managers

```python
with load_server("temp-server") as server:
    result = server.process(data="...")
# Process terminated, resources cleaned up
```

**Why:** Ensures server process cleanup even if exception raised.

## Limitations & Gotchas

**1. Sync wrapper overhead:** 
- Default executor wraps async in sync (event loop creation)
- For performance-critical code, use `aload_server()`

**2. Schema requirement for .data:**
- Servers without output schemas return `None` for .data
- Fallback to `.content` blocks
- Check `if result.data is not None` before using

**3. Tool transformation is shallow:**
- Only argument-level transformation
- Can't modify tool behavior/logic
- For complex changes, wrap in custom function

**4. Registry is per-machine:**
- Not synced across systems
- Check into git if team needs shared config
- Or use environment variables

**5. OAuth token expiry:**
- Auto-refresh on expiry
- If server changes OAuth config, delete `~/.config/functional-mcp/tokens.json`

## Performance Considerations

**Tool execution:**
- Sync version creates event loop per call (overhead)
- Use async for high-frequency calls
- Or keep event loop alive with custom client wrapper

**Resource caching:**
- Static resources cached after first access
- Dynamic resources fetched on each access
- Implement your own caching layer if needed

**Stub generation:**
- Generated once per command hash
- Cached to `~/.cache/functional-mcp/stubs/`
- No performance impact after first load

## Advanced Patterns

### Tool Selection Logic

```python
tools = server.tools

# Find tools that match criteria
search_tools = [
    tool for tool in tools
    if "search" in tool.name.lower()
    and len(tool.schema.required_args) <= 2
]

# Dynamic tool selection for agents
agent.add_tools([
    tool for tool in tools
    if tool.name in required_capabilities
])
```

### Schema-Driven Validation

```python
tool = server.tools.upload_file

# Validate before calling
required = set(tool.schema.required_args)
provided = set(user_inputs.keys())
missing = required - provided

if missing:
    raise ValueError(f"Missing: {missing}")

result = tool(**user_inputs)
```

### Reusable Transformations

```python
# Define transformation patterns
HIDE_LAT_LON = {
    "lat": ArgTransform(hide=True, default=25.7617),
    "lon": ArgTransform(hide=True, default=-80.1918),
}

# Apply to multiple tools
miami_weather = transform_tool(forecast, transform_args=HIDE_LAT_LON)
miami_restaurants = transform_tool(search_places, transform_args=HIDE_LAT_LON)
```
