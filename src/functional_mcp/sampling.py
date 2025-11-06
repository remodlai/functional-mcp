"""
LLM sampling handler using Remodl SDK.

When MCP servers request LLM completions, this module handles
those requests using the Remodl SDK instead of litellm.
"""

import os
from typing import Any, Callable


def create_sampling_handler() -> Callable:
    """
    Create default sampling handler using Remodl SDK.
    
    Auto-detects API keys and uses appropriate model.
    Priority: Remodl > Anthropic > OpenAI > Google
    
    Returns:
        Sampling handler function
    
    Raises:
        ImportError: If Remodl SDK not available
    """
    try:
        import remodl
    except ImportError:
        raise ImportError(
            "Remodl SDK required for sampling. Install with: pip install remodl-ai"
        )
    
    # Determine default model based on available keys
    def get_default_model() -> str:
        if os.getenv("REMODL_API_KEY"):
            return "remodl/remodl-chat-small"  # Your default model
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "claude-3-5-sonnet-20241022"
        elif os.getenv("OPENAI_API_KEY"):
            return "gpt-4o-mini"
        elif os.getenv("GOOGLE_API_KEY"):
            return "gemini-2.5-flash"
        else:
            raise ValueError(
                "No API keys found. Set REMODL_API_KEY, ANTHROPIC_API_KEY, "
                "OPENAI_API_KEY, or GOOGLE_API_KEY"
            )
    
    async def sampling_handler(
        messages: list[dict[str, Any]],
        model_prefs: dict[str, Any] | None = None,
        system_prompt: str | None = None,
        max_tokens: int = 1000,
    ) -> str:
        """
        Handle LLM sampling requests from MCP server.
        
        Args:
            messages: Chat messages
            model_prefs: Model preferences from server
            system_prompt: System prompt
            max_tokens: Max tokens to generate
        
        Returns:
            Generated text
        """
        # Prepare messages
        if system_prompt:
            full_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            full_messages = messages
        
        # Get model
        model = model_prefs.get("hints", {}).get("name") if model_prefs else None
        if not model:
            model = get_default_model()
        
        # Call Remodl SDK
        response = remodl.completion(
            model=model,
            messages=full_messages,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    return sampling_handler


def configure_sampling(model: str | None = None) -> None:
    """
    Configure global sampling settings.
    
    Args:
        model: Default model to use for sampling
    
    Example:
        from functional_mcp import configure_sampling
        
        configure_sampling(model="claude-3-5-sonnet-20241022")
    """
    # TODO: Store global sampling config
    pass


__all__ = ["create_sampling_handler", "configure_sampling"]

