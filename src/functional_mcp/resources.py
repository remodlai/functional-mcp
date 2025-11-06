"""
Resource access: MCP resources → Python attributes.

Converts MCP resources into properties or constants.
"""

from typing import Any


def create_resource_property(resource: Any, client: Any) -> property:
    """
    Create a property for accessing an MCP resource.
    
    Args:
        resource: MCP resource definition
        client: MCP client
    
    Returns:
        Property that fetches resource when accessed
    """
    
    @property
    def resource_prop(self):
        """Access MCP resource."""
        import asyncio
        
        async def _get():
            result = await client.read_resource(resource.uri)
            # Return first content block
            if result.contents:
                return result.contents[0].text if hasattr(result.contents[0], 'text') else result.contents[0]
            return None
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_get())
        finally:
            loop.close()
    
    resource_prop.__doc__ = resource.description or f"MCP resource: {resource.uri}"
    return resource_prop


__all__ = ["create_resource_property"]

