"""
Integration tests for functional-mcp.

Tests actual server loading and tool execution.
"""

import pytest
from functional_mcp import load_server
from functional_mcp.exceptions import MCPConnectionError


@pytest.mark.skip("Requires real MCP server")
def test_load_filesystem_server():
    """Test loading real filesystem server."""
    server = load_server("npx -y @modelcontextprotocol/server-filesystem /tmp")
    
    # Should have tools
    assert hasattr(server, 'tools')
    assert len(server.tools) > 0
    
    # Should be able to list tools
    tool_names = server.tools.list()
    assert isinstance(tool_names, list)
    
    server.close()


def test_load_invalid_server():
    """Test that invalid servers raise proper errors."""
    with pytest.raises(MCPConnectionError):
        server = load_server("this-command-does-not-exist")


@pytest.mark.skip("Requires real server")
def test_tool_execution():
    """Test actual tool execution."""
    server = load_server("npx -y @modelcontextprotocol/server-filesystem /tmp")
    
    # Get a tool
    list_dir = server.tools.list_directory
    
    # Check metadata
    assert list_dir.name
    assert list_dir.schema
    assert isinstance(list_dir.schema.required_args, list)
    
    # Execute
    result = list_dir(path="/tmp")
    assert result is not None
    
    server.close()


@pytest.mark.skip("Requires real server")  
def test_type_generation():
    """Test generateTypes() functionality."""
    import tempfile
    from pathlib import Path
    
    server = load_server("npx -y @modelcontextprotocol/server-filesystem /tmp")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "types.py"
        
        # Generate types
        result = server.tools.generateTypes(
            path=str(output_path),
            format='pydantic',
            only='input',
            with_instructions=True
        )
        
        # Should create file
        assert output_path.exists()
        
        # Should contain Pydantic code
        content = output_path.read_text()
        assert "from pydantic import BaseModel" in content
        assert "class" in content
    
    server.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

