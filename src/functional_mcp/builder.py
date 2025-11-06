"""
Server builder for fluent configuration API.

Enables clean, composable server configuration:
    load_server("cmd").disable('sampling').timeout(30)
"""

from __future__ import annotations

from typing import Any, Callable, Optional, List


class ServerBuilder:
    """
    Fluent builder for MCP server configuration.
    
    Examples:
        # Simple usage
        server = load_server("npx server")
        
        # With configuration
        server = load_server("npx server").disable('sampling', 'elicitation')
        
        # Chained configuration
        server = (load_server("https://api.example.com")
                  .headers({"Auth": "Bearer token"})
                  .timeout(60)
                  .allow('sampling'))
    """
    
    def __init__(self, command: str):
        self.command = command
        self._headers: Optional[dict[str, str]] = None
        self._roots: Optional[str | List[str]] = None
        self._on_sampling: Optional[Callable] = None
        self._on_elicitation: Optional[Callable] = None
        self._allow_sampling: bool = False  # Default: disabled
        self._allow_elicitation: bool = False  # Default: disabled
        self._auto_auth: bool = True
        self._timeout: float = 30.0
        self._server: Any = None  # Lazily loaded
    
    def headers(self, headers: dict[str, str]) -> ServerBuilder:
        """Set HTTP headers for remote servers."""
        self._headers = headers
        return self
    
    def roots(self, roots: str | List[str]) -> ServerBuilder:
        """Set directory roots for filesystem servers."""
        self._roots = roots
        return self
    
    def timeout(self, seconds: float) -> ServerBuilder:
        """Set request timeout in seconds."""
        self._timeout = seconds
        return self
    
    def allow(self, *features: str) -> ServerBuilder:
        """
        Enable features.
        
        Args:
            *features: Feature names ('sampling', 'elicitation', 'auth')
        
        Example:
            server = load_server("cmd").allow('sampling', 'elicitation')
        """
        for feature in features:
            if feature == 'sampling':
                self._allow_sampling = True
            elif feature == 'elicitation':
                self._allow_elicitation = True
            elif feature == 'auth':
                self._auto_auth = True
            else:
                raise ValueError(f"Unknown feature: {feature}")
        return self
    
    def disable(self, *features: str) -> ServerBuilder:
        """
        Disable features.
        
        Args:
            *features: Feature names ('sampling', 'elicitation', 'auth')
        
        Example:
            server = load_server("cmd").disable('sampling')
        """
        for feature in features:
            if feature == 'sampling':
                self._allow_sampling = False
            elif feature == 'elicitation':
                self._allow_elicitation = False
            elif feature == 'auth':
                self._auto_auth = False
            else:
                raise ValueError(f"Unknown feature: {feature}")
        return self
    
    def on_sampling(self, handler: Callable) -> ServerBuilder:
        """Set custom sampling handler."""
        self._on_sampling = handler
        return self
    
    def on_elicitation(self, handler: Callable) -> ServerBuilder:
        """Set custom elicitation handler."""
        self._on_elicitation = handler
        return self
    
    def _ensure_loaded(self) -> Any:
        """Lazy-load the actual server on first use."""
        if self._server is None:
            # Lazy import - only loaded when actually needed
            from ._impl import load_server_impl
            
            self._server = load_server_impl(
                command=self.command,
                headers=self._headers,
                roots=self._roots,
                on_sampling=self._on_sampling,
                on_elicitation=self._on_elicitation,
                allow_sampling=self._allow_sampling,
                allow_elicitation=self._allow_elicitation,
                auto_auth=self._auto_auth,
                timeout=self._timeout,
            )
        return self._server
    
    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to the loaded server."""
        # Ensure server is loaded
        server = self._ensure_loaded()
        return getattr(server, name)
    
    def __enter__(self) -> Any:
        """Context manager support."""
        return self._ensure_loaded().__enter__()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager support."""
        if self._server:
            return self._server.__exit__(exc_type, exc_val, exc_tb)
        return False


__all__ = ["ServerBuilder"]

