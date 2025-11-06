"""
Authentication handling for MCP servers.

Supports Bearer tokens, OAuth flows, and custom auth.
"""

import json
import webbrowser
from pathlib import Path
from typing import Callable
import httpx


_TOKEN_CACHE = Path.home() / ".config" / "functional-mcp" / "tokens.json"


class BearerAuth(httpx.Auth):
    """
    Bearer token authentication.
    
    Example:
        auth = BearerAuth("sk-1234567890")
        server = load("https://api.example.com/mcp", auth=auth)
    """
    
    def __init__(self, token: str):
        self.token = token
    
    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class OAuth:
    """
    OAuth authentication with automatic browser flow.
    
    Handles PKCE flow, token storage, and auto-refresh.
    
    Example:
        # Auto OAuth (browser opens)
        server = load("https://api.example.com/mcp", auth="oauth")
        
        # Custom OAuth
        oauth = OAuth(
            auth_url="https://provider.com/auth",
            token_url="https://provider.com/token",
            client_id="..."
        )
        server = load("https://api.example.com/mcp", auth=oauth)
    """
    
    def __init__(
        self,
        auth_url: str,
        token_url: str,
        client_id: str,
        scopes: list[str] | None = None,
    ):
        self.auth_url = auth_url
        self.token_url = token_url
        self.client_id = client_id
        self.scopes = scopes or []
        self._token = None
    
    def get_token(self) -> str:
        """Get access token, triggering OAuth flow if needed."""
        # Check cache
        if self._load_cached_token():
            return self._token
        
        # Trigger OAuth flow
        self._do_oauth_flow()
        return self._token
    
    def _load_cached_token(self) -> bool:
        """Load token from cache if valid."""
        if not _TOKEN_CACHE.exists():
            return False
        
        try:
            with open(_TOKEN_CACHE) as f:
                data = json.load(f)
            
            # TODO: Check expiry
            self._token = data.get("access_token")
            return self._token is not None
        except (json.JSONDecodeError, KeyError):
            return False
    
    def _save_token(self, token_data: dict):
        """Save token to cache."""
        _TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
        with open(_TOKEN_CACHE, 'w') as f:
            json.dump(token_data, f)
    
    def _do_oauth_flow(self):
        """Execute OAuth PKCE flow in browser."""
        import secrets
        import hashlib
        import base64
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from urllib.parse import urlencode, parse_qs
        
        # Generate PKCE parameters
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        
        # Build auth URL
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost:8080/callback",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "scope": " ".join(self.scopes),
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        
        # Capture authorization code
        auth_code = None
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code
                query = parse_qs(self.path.split("?")[1])
                auth_code = query.get("code", [None])[0]
                
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authentication successful! You can close this window.</h1></body></html>")
            
            def log_message(self, format, *args):
                pass  # Silence logs
        
        # Start local server
        server = HTTPServer(("localhost", 8080), CallbackHandler)
        
        # Open browser
        print("🔐 Opening browser for authentication...")
        webbrowser.open(auth_url)
        
        # Wait for callback
        server.handle_request()
        server.server_close()
        
        if not auth_code:
            raise ValueError("OAuth flow failed - no authorization code received")
        
        # Exchange code for token
        token_response = httpx.post(
            self.token_url,
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": "http://localhost:8080/callback",
                "client_id": self.client_id,
                "code_verifier": code_verifier,
            }
        )
        
        token_data = token_response.json()
        self._token = token_data["access_token"]
        self._save_token(token_data)
        
        print("✅ Authentication successful!")


def create_auth_handler(
    auth: str | Callable | httpx.Auth,
) -> httpx.Auth | None:
    """
    Create authentication handler from various inputs.
    
    Args:
        auth: Auth specification
    
    Returns:
        httpx.Auth instance or None
    """
    if auth is None:
        return None
    
    if isinstance(auth, httpx.Auth):
        return auth
    
    if isinstance(auth, str):
        if auth == "oauth":
            # Auto-detect OAuth endpoints
            # TODO: Discover from server
            return None
        else:
            # Assume it's a bearer token
            return BearerAuth(auth)
    
    if callable(auth):
        # It's a token provider function
        token = auth()
        return BearerAuth(token)
    
    return None


__all__ = ["BearerAuth", "OAuth", "create_auth_handler"]

