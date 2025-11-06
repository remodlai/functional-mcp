"""
Dynamic server class generation.

Creates a Python class where MCP tools become methods,
resources become properties, and prompts become template functions.
"""

from typing import Any, Callable
from functools import wraps


def create_server_class(
    name: str,
    tools: list[Any],
    resources: list[Any],
    prompts: list[Any],
    client: Any,
    sampling_handler: Callable | None,
    elicitation_handler: Callable | None,
) -> type:
    """
    Generate a dynamic server class with tools/resources/prompts.
    
    Tools become methods, resources become properties/constants,
    prompts become template functions.
    
    Args:
        name: Server name
        tools: List of MCP tool definitions
        resources: List of MCP resource definitions
        prompts: List of MCP prompt definitions
        client: FastMCP Client instance
        sampling_handler: Handler for LLM requests
        elicitation_handler: Handler for user input
    
    Returns:
        Dynamic server class
    """
    
    # Convert tool names to snake_case
    def to_snake_case(name: str) -> str:
        """Convert camelCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    # Create class dict
    class_dict = {
        "_client": client,
        "_tools_map": {},
        "_resources_map": {},
        "_prompts_map": {},
        "tools": [],  # For AI SDK integration
    }
    
    # Add tools as methods
    for tool in tools:
        tool_name = tool.name
        method_name = to_snake_case(tool_name)
        
        # Store original tool
        class_dict["_tools_map"][method_name] = tool
        
        # Create method
        def create_tool_method(t):
            @wraps(lambda: None)  # Placeholder for proper wrapping
            async def tool_method(self, **kwargs):
                """Execute MCP tool."""
                try:
                    result = await self._client.call_tool(t.name, kwargs)
                    return result.content
                except Exception as e:
                    from .exceptions import MCPToolError
                    raise MCPToolError(t.name, str(e), e) from e
            
            # Set metadata
            tool_method.__name__ = method_name
            tool_method.__doc__ = t.description or f"MCP tool: {t.name}"
            
            # For AI SDKs - callable version
            def sdk_callable(**kwargs):
                """Sync wrapper for AI SDKs."""
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(tool_method(None, **kwargs))
                finally:
                    loop.close()
            
            sdk_callable.__name__ = method_name
            sdk_callable.__doc__ = tool_method.__doc__
            
            return tool_method, sdk_callable
        
        method, sdk_method = create_tool_method(tool)
        class_dict[method_name] = method
        class_dict["tools"].append(sdk_method)
    
    # Add resources as properties
    for resource in resources:
        resource_uri = resource.uri
        resource_name = resource.name or resource_uri.split("/")[-1]
        
        # Static resources → UPPER_CASE
        # Dynamic resources → lowercase properties
        is_static = not resource.uri.startswith(("dynamic://", "live://"))
        
        if is_static:
            prop_name = to_snake_case(resource_name).upper()
        else:
            prop_name = to_snake_case(resource_name)
        
        class_dict["_resources_map"][prop_name] = resource
        
        def create_resource_property(res):
            @property
            def resource_prop(self):
                """Access MCP resource."""
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    async def _get():
                        result = await self._client.read_resource(res.uri)
                        return result.contents
                    return loop.run_until_complete(_get())
                finally:
                    loop.close()
            
            resource_prop.__doc__ = res.description or f"MCP resource: {res.uri}"
            return resource_prop
        
        class_dict[prop_name] = create_resource_property(resource)
    
    # Add prompts as template functions
    for prompt in prompts:
        prompt_name = to_snake_case(prompt.name)
        class_dict["_prompts_map"][prompt_name] = prompt
        
        def create_prompt_function(p):
            async def prompt_fn(self, **kwargs):
                """Get formatted prompt."""
                result = await self._client.get_prompt(p.name, kwargs)
                return result.messages
            
            prompt_fn.__name__ = prompt_name
            prompt_fn.__doc__ = p.description or f"MCP prompt: {p.name}"
            return prompt_fn
        
        class_dict[prompt_name] = create_prompt_function(prompt)
    
    # Add context manager support
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def close(self):
        """Close the server connection."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._client.__aexit__(None, None, None))
        finally:
            loop.close()
    
    class_dict["__enter__"] = __enter__
    class_dict["__exit__"] = __exit__
    class_dict["close"] = close
    
    # Create the class
    server_class = type(
        f"{name.replace(' ', '')}Server",
        (object,),
        class_dict
    )
    
    return server_class


__all__ = ["create_server_class"]

