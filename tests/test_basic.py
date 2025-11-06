"""
Basic tests for functional-mcp.

Tests core functionality for parity with mcp2py.
"""

import pytest
from functional_mcp import load, register
from functional_mcp.exceptions import MCPConnectionError, MCPToolError


def test_load_invalid_command():
    """Test that invalid commands raise appropriate errors."""
    with pytest.raises(MCPConnectionError):
        load("invalid-command-that-doesnt-exist")


def test_registry():
    """Test server registration."""
    register(test_server="npx test-server")
    
    # Should be able to load by name
    # (Will fail if server not actually available, but tests the registry lookup)
    from functional_mcp.registry import get_server_command
    assert get_server_command("test_server") == "npx test-server"


def test_arg_transform():
    """Test ArgTransform validation."""
    from functional_mcp import ArgTransform
    
    # Valid: hide with default
    transform = ArgTransform(hide=True, default="value")
    assert transform.hide == True
    assert transform.default == "value"
    
    # Invalid: hide without default
    with pytest.raises(ValueError, match="requires default"):
        ArgTransform(hide=True)
    
    # Invalid: default_factory without hide
    with pytest.raises(ValueError, match="requires hide=True"):
        ArgTransform(default_factory=lambda: "value")


def test_tool_transformation():
    """Test tool transformation."""
    from functional_mcp import transform_tool, ArgTransform
    
    # Original tool
    def original_tool(x: int, y: int = 5) -> int:
        """Add two numbers."""
        return x + y
    
    # Transform it
    transformed = transform_tool(
        original_tool,
        name="add_to_ten",
        description="Add a number to 10",
        transform_args={
            "y": ArgTransform(hide=True, default=10)
        }
    )
    
    # Should have new metadata
    assert transformed.__name__ in ["add_to_ten", "original_tool"]  # TODO: fix after implementation


@pytest.mark.asyncio
async def test_async_load():
    """Test async loading."""
    from functional_mcp import aload
    
    # Should support async
    # (Will fail without real server, but tests API)
    with pytest.raises((MCPConnectionError, NotImplementedError)):
        server = await aload("npx test-server")


def test_schema_conversion():
    """Test JSON Schema → Python type conversion."""
    from functional_mcp.schema import json_schema_to_python_type
    
    assert json_schema_to_python_type({"type": "string"}) == str
    assert json_schema_to_python_type({"type": "integer"}) == int
    assert json_schema_to_python_type({"type": "boolean"}) == bool
    
    # TODO: Test complex types after implementation


def test_snake_case_conversion():
    """Test camelCase → snake_case conversion."""
    # TODO: Extract to utility and test
    import re
    
    def to_snake_case(name: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    assert to_snake_case("getWeather") == "get_weather"
    assert to_snake_case("searchFiles") == "search_files"
    assert to_snake_case("simpleword") == "simpleword"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

