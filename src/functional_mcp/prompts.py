"""
Prompt templates: MCP prompts → Python functions.

Converts MCP prompts into callable template functions.
"""

from typing import Any


def create_prompt_function(prompt: Any, client: Any) -> callable:
    """
    Create a function for an MCP prompt.
    
    Args:
        prompt: MCP prompt definition
        client: FastMCP client
    
    Returns:
        Function that returns formatted prompt
    """
    
    async def prompt_fn(**kwargs) -> str:
        """Get formatted prompt from server."""
        import asyncio
        
        result = await client.get_prompt(prompt.name, kwargs)
        
        # Format messages into string
        if hasattr(result, 'messages'):
            parts = []
            for msg in result.messages:
                role = msg.role
                content = msg.content
                parts.append(f"{role}: {content}")
            return "\n".join(parts)
        
        return str(result)
    
    # Make sync wrapper
    def sync_prompt_fn(**kwargs) -> str:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(prompt_fn(**kwargs))
        finally:
            loop.close()
    
    sync_prompt_fn.__name__ = prompt.name
    sync_prompt_fn.__doc__ = prompt.description or f"MCP prompt: {prompt.name}"
    
    return sync_prompt_fn


__all__ = ["create_prompt_function"]

