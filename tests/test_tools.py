"""
Tests for tool functionality.

Tests Tool, ToolCollection, and ToolSchema classes.
"""

import pytest
from functional_mcp.tools import Tool, ToolCollection, ToolSchema, create_tool


def test_tool_schema_to_dict():
    """Test ToolSchema.toDict() method."""
    schema = ToolSchema(
        name="search",
        description="Search for items",
        input_schema={"properties": {"query": {"type": "string"}}},
        required_args=["query"],
        optional_args=["limit"]
    )
    
    result = schema.toDict()
    
    assert result["name"] == "search"
    assert result["description"] == "Search for items"
    assert "query" in result["required"]
    assert "limit" in result["optional"]


def test_tool_collection_name_access():
    """Test accessing tools by name."""
    
    # Mock tool
    mock_tool = Tool(
        name="search",
        description="Search tool",
        input_schema={"properties": {}},
        executor=lambda **kwargs: "result"
    )
    
    collection = ToolCollection({"search": mock_tool})
    
    # Access by name
    search = collection.search
    assert search.name == "search"
    
    # Access via get()
    search2 = collection.get("search")
    assert search2 is not None
    assert search2.name == "search"
    
    # Missing tool
    missing = collection.get("nonexistent")
    assert missing is None


def test_tool_collection_list():
    """Test listing tool names."""
    tools = {
        "search": Tool("search", "desc", {}, lambda: None),
        "upload": Tool("upload", "desc", {}, lambda: None),
    }
    
    collection = ToolCollection(tools)
    
    names = collection.list()
    assert "search" in names
    assert "upload" in names
    assert len(names) == 2


def test_tool_collection_iteration():
    """Test iterating over tools."""
    tools = {
        "search": Tool("search", "desc", {}, lambda: None),
        "upload": Tool("upload", "desc", {}, lambda: None),
    }
    
    collection = ToolCollection(tools)
    
    tool_list = list(collection)
    assert len(tool_list) == 2
    assert all(isinstance(t, Tool) for t in tool_list)


def test_tool_tags_extraction():
    """Test that tags are extracted from meta."""
    tool = Tool(
        name="test",
        description="desc",
        input_schema={},
        executor=lambda: None,
        meta={"_fastmcp": {"tags": ["search", "database"]}}
    )
    
    assert tool.tags == ["search", "database"]


def test_tool_tags_missing():
    """Test tools without tags."""
    tool = Tool(
        name="test",
        description="desc",
        input_schema={},
        executor=lambda: None,
        meta={}
    )
    
    assert tool.tags == []


def test_arg_transform_validation():
    """Test ArgTransform validation rules."""
    from functional_mcp import ArgTransform
    
    # Valid: hide with default
    t1 = ArgTransform(hide=True, default="value")
    assert t1.hide == True
    
    # Invalid: hide without default
    with pytest.raises(ValueError, match="requires default"):
        ArgTransform(hide=True)
    
    # Invalid: default_factory without hide
    with pytest.raises(ValueError, match="requires hide=True"):
        ArgTransform(default_factory=lambda: "value")
    
    # Invalid: both default and default_factory
    # Pydantic catches default_factory without hide first
    with pytest.raises(Exception):  # Could be ValueError or ValidationError
        ArgTransform(default="a", default_factory=lambda: "b")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

