# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**functional-mcp** transforms any MCP (Model Context Protocol) server into a native Python module automatically. The core philosophy: "Every MCP server becomes native Python. Automatically."

**Key Innovation:** Dynamic class generation that converts MCP tools → methods, resources → properties, and prompts → functions with full IDE support and type safety.

## Development Commands

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tools.py

# Run with verbose output
pytest -v

# Run integration tests (currently marked as skip)
pytest tests/test_integration.py

# Type checking
mypy src/functional_mcp
```

### Package Management
```bash
# Install development dependencies
pip install -e ".[dev]"

# Build package
python -m build
```

## High-Level Architecture

### Core Design Pattern: Dynamic Class Generation

The library uses Python's `type()` to generate classes at runtime. Each MCP server becomes a unique Python class with:

1. **Tools** → Callable methods + ToolCollection with metadata
2. **Resources** → Lazy-loaded properties
3. **Prompts** → Template functions

### Critical Data Flow

```
MCP Server (any type)
    ↓
FastMCP Client Connection (auto-detects transport)
    ↓
Dynamic Class Generation (server.py)
    ↓
Python Module with Full IDE Support
```

### Three-Tier Tool System

The most important architectural component is the tool object system in `src/tools.py`:

1. **ToolSchema** - Pure metadata (name, description, JSON schema, required/optional args)
2. **Tool** - Callable object with metadata, schema, tags, and execution logic
3. **ToolCollection** - Dictionary-like container exposing tools as both attributes and methods

**Dual Access Pattern:**
```python
# Direct method call (simple)
server.search(query="test")

# Via ToolCollection (with metadata)
server.tools.search.schema.toDict()  # Get schema
server.tools.search(query="test")     # Execute
```

### Four Major MCP Object Types

When making changes that affect any one type, consider applying to all:

- **Tools** (`src/tools.py`) - Callable operations
- **Resources** (`src/resources.py`) - Data access
- **Resource Templates** (`src/resources.py`) - Parameterized resources
- **Prompts** (`src/prompts.py`) - Template functions

Each type has an associated Manager class that handles lifecycle and execution.

### Async-to-Sync Bridge Pattern

FastMCP is async-only, but the library provides a sync API:

```python
def executor(**kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(async_executor(**kwargs))
    finally:
        loop.close()
```

This pattern is used throughout `client.py` to wrap FastMCP's async methods.

## Key Module Relationships

### Entry Point Chain
- `loader.py` - Entry point (`load_server()`, `aload_server()`)
  - Detects transport type (npx → NpxStdioTransport, URLs → StreamableHttpTransport, etc.)
  - Creates FastMCP Client
  - Delegates to `create_server_class()` in `server.py`

### Server Class Generation
- `server.py` - Dynamic class generation
  - Imports: `tools.py`, `schema.py`
  - Creates: Tool objects, ToolCollection
  - Generates: Dynamic class using `type()` at runtime

### Tool System
- `tools.py` - Core tool implementation
  - Defines: Tool, ToolCollection, ToolSchema
  - Uses: `schema.py` for type conversion
  - Delegates: `codegen.py` for `generateTypes()`
  - Calls: `client.call_tool()` via executor

### Type Conversion
- `schema.py` - Bidirectional JSON Schema ↔ Python types
  - Used by: `tools.py`, `codegen.py`, `stubs.py`
  - Enables: IDE autocomplete and type checking

### Code Generation
- `codegen.py` - Type generation (Pydantic, dataclass, TypeScript)
  - Called by: `ToolCollection.generateTypes()`
  - Generates: Type definitions from tool schemas

## Implementation Status

**Phase 1 (Core):** ✅ Complete
- Basic connection, tool/resource/prompt mapping, exceptions

**Phase 2 (Advanced):** ✅ Complete
- LLM sampling (Remodl SDK), elicitation, OAuth, registry, type generation

**Phase 3 (Enhancements):** 🚧 In Progress
- `ArgTransform` class: ✅ Complete with validation
- `transform_tool()` function: ⏳ Skeleton only (needs implementation)
- Remodl integration helpers: ⏳ Not started
- Tool chaining: ⏳ Not started

## Important Design Decisions

1. **FastMCP over raw MCP** - Higher-level abstraction, better error handling
2. **Remodl SDK over litellm** - Better ecosystem integration (`sampling.py`)
3. **Pydantic everywhere** - Consistent data validation
4. **Metadata-first tools** - Enables AI SDK introspection and IDE support
5. **Snake case conversion** - `getWeather` → `get_weather` for Python idioms

## Tool Transformation System

The `ArgTransform` class in `transformation.py` provides declarative argument customization:

```python
ArgTransform(
    name=None,              # Rename argument
    description=None,       # Update description
    default=None,           # Set default value
    default_factory=None,   # Lazy default generation
    hide=True,              # Hide from LLM (requires default)
    required=None,          # Force requirement
    type=None               # Change type
)
```

**Validation Rules:**
- Can't use `default_factory` without `hide=True`
- Can't `hide=True` without `default` or `default_factory`
- Can't specify both `default` and `default_factory`

**Note:** `transform_tool()` is currently a skeleton and returns the original tool unchanged. Full implementation is pending.

## Exception Hierarchy

All exceptions inherit from `MCPError`:
- `MCPConnectionError` - Failed to connect
- `MCPToolError` - Tool execution failed (includes `.tool_name`, `.original_error`)
- `MCPResourceError` - Resource access failed
- `MCPValidationError` - Invalid arguments (includes `.errors` dict)
- `MCPSamplingError` - LLM sampling failed
- `MCPAuthenticationError` - Auth failed
- `MCPElicitationError` - User input failed

Capture context (tool_name, errors dict) for better debugging.

## Testing Strategy

**Unit Tests:** Mock MCP servers, test all parameter combinations
**Integration Tests:** Currently marked `@pytest.mark.skip` - require real MCP servers
**Target Servers:** filesystem, memory, weather MCP servers

When writing tests:
- Use `pytest` with `asyncio_mode = "auto"`
- Mock tools/resources for unit tests
- Include realistic error scenarios
- Verify both sync and async APIs

## Security Considerations

Three-layer security system:

1. **OAuth (`auth.py`)** - PKCE flow, token storage in `~/.config/functional-mcp/tokens.json`
2. **LLM Sampling (`sampling.py`)** - Controllable via `allow_sampling=False`
3. **User Input (`elicitation.py`)** - Controllable via `allow_elicitation=False`

Token auto-refresh is handled automatically. Custom auth handlers support Bearer, OAuth, and Callable patterns.

## File Organization

```
src/functional_mcp/
├── __init__.py              # Public API exports
├── loader.py                # Entry point: load_server(), aload_server()
├── client.py                # FastMCP wrapper (sync/async bridge)
├── server.py                # Dynamic class generation
├── tools.py                 # Tool objects with metadata ⭐
├── resources.py             # Resource → property mapping
├── prompts.py               # Prompt → function mapping
├── schema.py                # JSON Schema ↔ Python type conversion
├── transformation.py        # Tool customization (ArgTransform)
├── codegen.py               # Type generation (Pydantic/dataclass/TS)
├── registry.py              # Server registration (~/.config/)
├── exceptions.py            # 7 custom exception types
├── sampling.py              # LLM sampling (Remodl SDK)
├── elicitation.py           # User input handling
├── auth.py                  # OAuth/authentication flows
├── roots.py                 # Filesystem roots management
├── stubs.py                 # .pyi stub generation
└── transports/              # Transport re-exports from FastMCP
```

## Python Version

Requires **Python 3.12+** (see `.python-version` and `pyproject.toml`)

## Dependencies

- `fastmcp>=2.10.0` - Core MCP client
- `pydantic>=2.0.0` - Data validation & models
- `httpx>=0.27.0` - HTTP client for remote servers

Dev dependencies: `pytest`, `pytest-asyncio`, `mypy`
