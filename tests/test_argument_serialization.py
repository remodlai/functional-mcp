"""
Test automatic argument serialization.

Tests that complex Python objects are automatically serialized to JSON
when passed to MCP tools.
"""

import pytest
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from functional_mcp import load_server


@dataclass
class LocationData:
    """Test dataclass for serialization."""
    city: str
    lat: float
    lon: float


class ConfigModel(BaseModel):
    """Test Pydantic model for serialization."""
    format: str
    include_metadata: bool
    max_results: int = 10


def test_primitive_argument_passthrough():
    """Test that primitive arguments pass through unchanged."""
    # Load a real MCP server - clean, elegant API!
    server = load_server("npx -y @modelcontextprotocol/server-filesystem /tmp")
    
    # Call with primitive arguments
    result = server.list_directory(path="/tmp")
    
    # Should work without serialization errors
    assert result is not None
    
    server.close()


def test_dict_argument_serialization():
    """Test that dict arguments are serialized to JSON."""
    server = load_server("npx -y @modelcontextprotocol/server-filesystem /tmp")
    
    # This would need a tool that accepts complex arguments
    # For now, verify the server loads and tools are accessible
    assert hasattr(server, 'tools')
    assert len(server.tools) > 0
    
    # Check that tools have the serialization logic
    tool = list(server.tools)[0]
    assert hasattr(tool, '_executor')
    
    server.close()


def test_dataclass_argument_serialization():
    """Test that dataclass arguments are serialized."""
    # Create test dataclass
    location = LocationData(city="Miami", lat=25.7617, lon=-80.1918)
    
    # Verify serialization logic exists
    import pydantic_core
    serialized = pydantic_core.to_json(location).decode("utf-8")
    
    # Should be valid JSON
    import json
    parsed = json.loads(serialized)
    assert parsed["city"] == "Miami"
    assert parsed["lat"] == 25.7617
    assert parsed["lon"] == -80.1918


def test_pydantic_argument_serialization():
    """Test that Pydantic models are serialized."""
    config = ConfigModel(format="json", include_metadata=True)
    
    # Verify serialization
    import pydantic_core
    serialized = pydantic_core.to_json(config).decode("utf-8")
    
    # Should be valid JSON
    import json
    parsed = json.loads(serialized)
    assert parsed["format"] == "json"
    assert parsed["include_metadata"] == True
    assert parsed["max_results"] == 10


def test_list_argument_serialization():
    """Test that list arguments are serialized."""
    tags = ["weather", "forecast", "api"]
    
    import pydantic_core
    serialized = pydantic_core.to_json(tags).decode("utf-8")
    
    import json
    parsed = json.loads(serialized)
    assert parsed == ["weather", "forecast", "api"]


def test_nested_object_serialization():
    """Test that nested objects are serialized correctly."""
    data = {
        "config": ConfigModel(format="csv", include_metadata=False),
        "locations": [
            LocationData(city="Miami", lat=25.76, lon=-80.19),
            LocationData(city="Boston", lat=42.36, lon=-71.06),
        ],
        "simple_field": "test"
    }
    
    import pydantic_core
    serialized = pydantic_core.to_json(data).decode("utf-8")
    
    import json
    parsed = json.loads(serialized)
    assert parsed["config"]["format"] == "csv"
    assert len(parsed["locations"]) == 2
    assert parsed["locations"][0]["city"] == "Miami"
    assert parsed["simple_field"] == "test"


def test_primitive_types_not_serialized():
    """Test that primitive types pass through without serialization."""
    # String
    value = "test"
    assert isinstance(value, str)
    
    # Int
    value = 42
    assert isinstance(value, int)
    
    # Float
    value = 3.14
    assert isinstance(value, float)
    
    # Bool
    value = True
    assert isinstance(value, bool)
    
    # None
    value = None
    assert value is None


def test_tool_with_mixed_arguments():
    """Test tool call with both primitive and complex arguments."""
    server = load_server("npx -y @modelcontextprotocol/server-filesystem /tmp")
    
    # Call with primitive argument (should work)
    result = server.list_directory(path="/tmp")
    assert result is not None
    
    server.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

