# functional-mcp Implementation Plan

## Goal
Achieve feature parity with mcp2py, then enhance with FastMCP tool transformation.

## Phase 1: Core Functionality (Must Have for Parity)

### 1.1 Basic Connection
- [x] `load(command)` - Connect to stdio MCP servers
- [x] `load(url)` - Connect to HTTP/SSE MCP servers  
- [x] `aload()` - Async version (basic implementation)
- [x] Context manager support (`with load()`)
- [x] Process management (start/stop servers)

**Files:**
- ✅ `src/functional_mcp/loader.py` - Complete
- ✅ `src/functional_mcp/client.py` - Complete (sync/async bridge)

### 1.2 Tool Mapping
- [x] Tools → Python methods (snake_case conversion)
- [x] Type hints from JSON Schema
- [x] Docstrings from tool descriptions
- [x] Return type: `dict[str, Any]`
- [x] `.tools` property (list for AI SDKs)

**Files:**
- ✅ `src/functional_mcp/tools.py` - Complete
- ✅ `src/functional_mcp/schema.py` - Complete (bidirectional conversion)

### 1.3 Resource Access
- [x] Static resources → UPPER_CASE constants
- [x] Dynamic resources → lowercase properties
- [x] Resource caching
- [x] `.resources` property

**Files:**
- ✅ `src/functional_mcp/resources.py` - Complete

### 1.4 Prompt Templates
- [x] Prompts → Template functions
- [x] Argument interpolation
- [x] Return formatted strings
- [x] `.prompts` property

**Files:**
- ✅ `src/functional_mcp/prompts.py` - Complete

### 1.5 Exception Handling
- [x] `MCPConnectionError`
- [x] `MCPToolError`
- [x] `MCPResourceError`
- [x] `MCPValidationError`
- [x] `MCPSamplingError`
- [x] `MCPAuthenticationError`
- [x] `MCPElicitationError`

**Files:**
- ✅ `src/functional_mcp/exceptions.py` - Complete

## Phase 2: Advanced Features (Parity)

### 2.1 Sampling (LLM Support)
- [x] Default sampling handler
- [x] Auto-detect API keys (REMODL, ANTHROPIC, OPENAI, GOOGLE)
- [x] Custom sampling callbacks
- [x] `allow_sampling=False` option

**Files:**
- ✅ `src/functional_mcp/sampling.py` - Complete

**Uses:** ✅ Remodl SDK instead of litellm

### 2.2 Elicitation (User Input)
- [x] Terminal prompts (default)
- [x] Custom elicitation callbacks
- [x] Type-aware prompts (bool → y/n, etc.)
- [x] `allow_elicitation=False` option
- [x] Pre-filled answers (`ElicitationDefaults`)

**Files:**
- ✅ `src/functional_mcp/elicitation.py` - Complete

### 2.3 OAuth Authentication
- [x] Auto browser flow (PKCE)
- [x] Token storage (`~/.config/functional-mcp/tokens.json`)
- [x] Auto token refresh
- [x] Custom auth handlers (Bearer, OAuth, Callable)
- [x] `auto_auth=False` option

**Files:**
- ✅ `src/functional_mcp/auth.py` - Complete

### 2.4 Roots Management
- [x] `roots` parameter in load()
- [x] `.set_roots()` method (via server class)
- [x] Multiple directory support

**Files:**
- ✅ `src/functional_mcp/roots.py` - Complete

### 2.5 Server Registry
- [x] `register(name=command)` - Save servers
- [x] Load by name: `load("weather")`
- [x] Registry storage: `~/.config/functional-mcp/servers.json`

**Files:**
- ✅ `src/functional_mcp/registry.py` - Complete

### 2.6 Type Generation & IDE Support
- [x] Auto-generate `.pyi` stub files
- [x] Cache to `~/.cache/functional-mcp/stubs/`
- [x] `.generate_stubs(path)` method
- [x] Full type hints for autocomplete

**Files:**
- ✅ `src/functional_mcp/stubs.py` - Complete

### 2.7 Transport Support
- [x] stdio transport (subprocess)
- [x] HTTP/SSE transport
- [x] Custom headers for auth
- [x] Re-exports from FastMCP

**Files:**
- ✅ `src/functional_mcp/transports/__init__.py` - Complete (re-exports)

## Phase 3: FastMCP Enhancements (Beyond Parity)

### 3.1 Tool Transformation
- [x] `ArgTransform` class (with validation)
- [x] Rename arguments
- [x] Hide arguments (with defaults)
- [x] Transform descriptions
- [x] Transform types
- [x] Transform default values
- [ ] Full transformation implementation (skeleton done)

**Files:**
- ✅ `src/functional_mcp/transformation.py` - ArgTransform complete, transform_tool skeleton

### 3.2 Enhanced Tool Creation
- [x] `transform_tool(tool, **transforms)` - API defined
- [ ] Reusable argument patterns - TODO
- [ ] Chaining transformations - TODO
- [ ] Context-aware factories - TODO

### 3.3 Remodl Integration
- [x] Auto-use Remodl SDK for sampling
- [ ] `.to_remodl_agent()` helper - TODO
- [ ] A2A model card generation - TODO

**Files:**
- Planned: `src/functional_mcp/integrations/remodl.py`

## Status: ✅ Core Complete, Ready for Testing

**Completed:**
- All Phase 1 modules (core functionality)
- All Phase 2 modules (advanced features)
- ArgTransform class and validation
- Package structure and documentation
- Example usage code
- Basic tests

**Next Steps:**
1. Test with real MCP servers
2. Complete transform_tool() implementation
3. Add Remodl integration helpers
4. Publish to PyPI

## Module Structure

```
functional_mcp/
├── __init__.py              # Public API: load, aload, register, configure
├── loader.py                # load() and aload() functions
├── client.py                # Core MCP client wrapper
├── server.py                # Dynamic server class generation
├── tools.py                 # Tool → method mapping
├── resources.py             # Resource → attribute mapping
├── prompts.py               # Prompt → function mapping
├── schema.py                # JSON Schema → Python types
├── stubs.py                 # .pyi stub generation
├── exceptions.py            # Custom exceptions
├── registry.py              # Server registry
├── sampling.py              # LLM sampling (uses Remodl)
├── elicitation.py           # User input handling
├── auth.py                  # OAuth flows
├── roots.py                 # Roots management
├── transformation.py        # Tool transformation (FastMCP-style)
├── transports/
│   ├── __init__.py
│   ├── stdio.py            # Subprocess transport
│   └── http.py             # HTTP/SSE transport
└── integrations/
    ├── __init__.py
    └── remodl.py           # Remodl SDK helpers
```

## Testing Strategy

### Unit Tests
- Each module has corresponding test file
- Mock MCP servers for testing
- Test all parameter combinations

### Integration Tests
- Test with real MCP servers:
  - `@modelcontextprotocol/server-filesystem`
  - `@modelcontextprotocol/server-memory`
  - `@h1deya/mcp-server-weather`

### Compatibility Tests
- Verify parity with mcp2py behavior
- Same inputs → same outputs
- Same error handling

## Success Criteria

### Parity Achieved When:
✅ All mcp2py examples work with functional-mcp (just swap import)
✅ Same API surface (`load`, `aload`, `register`, etc.)
✅ Same OAuth behavior
✅ Same sampling behavior (but using Remodl)
✅ Same elicitation behavior
✅ Same stub generation
✅ Same error types

### Enhanced When:
✅ Tool transformation works
✅ FastMCP integration complete
✅ Remodl helpers added
✅ Better documentation
✅ Cleaner implementation

## Development Order

1. **Core** (Phase 1.1-1.5) - Get basic load() working
2. **Advanced** (Phase 2.1-2.7) - Add all mcp2py features
3. **Enhance** (Phase 3) - Add FastMCP capabilities
4. **Polish** - Documentation, tests, examples

## Key Design Decisions

1. **Use FastMCP Client** - Not raw mcp library
2. **Use Remodl SDK** - For sampling, not litellm
3. **Keep mcp2py API** - For easy migration
4. **Add transformation** - As optional enhancement
5. **Pydantic everywhere** - Consistent with ecosystem

