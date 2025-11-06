"""
Configuration builder for MCP transports.

Provides fluent API for building, persisting, and loading transport configurations.
"""

import json
from pathlib import Path
from typing import Any, Dict, Literal
from pydantic import BaseModel


_CONFIG_DIR = Path.home() / ".config" / "functional-mcp" / "configs"

TransportType = Literal["stdio", "http", "python", "node", "uv", "uvx", "npx"]


class StdioConfig(BaseModel):
    """
    Configuration for MCP transports.
    
    Handles transport-type-specific serialization.
    
    Attributes:
        name: Config name
        transport_type: Transport type
        env: Environment variables (for python, node, stdio)
        env_vars: Environment variables (for npx, uv, uvx)
        cwd: Working directory
        args: Additional command arguments
        keep_alive: Keep subprocess alive between connections
        log_file: Path for stderr logging
        python_cmd: Python executable path (python only)
        python_version: Python version (uv, uvx only)
        with_packages: Additional packages (uv, uvx only)
    """
    
    name: str
    transport_type: TransportType
    
    # Common options
    env: Dict[str, str] = {}  # For python, node, stdio
    env_vars: Dict[str, str] = {}  # For npx, uv, uvx
    cwd: str | None = None
    args: list[str] = []
    keep_alive: bool = True
    log_file: str | None = None
    
    # Type-specific options
    python_cmd: str | None = None  # PythonStdioTransport
    python_version: str | None = None  # UvStdioTransport, UvxStdioTransport
    with_packages: list[str] = []  # UvStdioTransport, UvxStdioTransport
    
    def to_transport_kwargs(self) -> Dict[str, Any]:
        """
        Generate kwargs for transport instantiation.
        
        Maps config to transport-specific parameter names.
        
        Returns:
            Dict of kwargs for transport __init__
        """
        kwargs: Dict[str, Any] = {}
        
        if self.transport_type in ["npx", "uv", "uvx"]:
            # These transports use env_vars, not env
            if self.env_vars:
                kwargs["env_vars"] = self.env_vars
        else:
            # python, node, stdio use env
            if self.env:
                kwargs["env"] = self.env
        
        if self.cwd:
            kwargs["cwd"] = self.cwd
        
        if self.args:
            kwargs["args"] = self.args
        
        if not self.keep_alive:  # Only set if False (True is default)
            kwargs["keep_alive"] = self.keep_alive
        
        if self.log_file:
            kwargs["log_file"] = Path(self.log_file)
        
        # Type-specific options
        if self.transport_type == "python" and self.python_cmd:
            kwargs["python_cmd"] = self.python_cmd
        
        if self.transport_type in ["uv", "uvx"]:
            if self.python_version:
                kwargs["python_version"] = self.python_version
            if self.with_packages:
                kwargs["with_packages"] = self.with_packages
        
        return kwargs
    
    def save(self) -> Path:
        """
        Save config to disk.
        
        Returns:
            Path where config was saved
        """
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        path = _CONFIG_DIR / f"{self.name}.json"
        path.write_text(self.model_dump_json(indent=2))
        return path
    
    @classmethod
    def load(cls, name: str) -> "StdioConfig":
        """
        Load config from disk.
        
        Args:
            name: Config name
        
        Returns:
            StdioConfig object
        
        Raises:
            FileNotFoundError: If config doesn't exist
        """
        path = _CONFIG_DIR / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Config '{name}' not found at {path}")
        
        data = json.loads(path.read_text())
        return cls(**data)


class ConfigBuilder:
    """
    Fluent builder for transport configurations.
    
    Example:
        # Fluent style
        config = (create_config("prod", transport_type="python")
                 .add_env("API_KEY").with_value("secret")
                 .add_env("DB_HOST").with_value("prod.db.com")
                 .python_cmd("/usr/bin/python3.11")
                 .init())
        
        # Dict style
        config = (create_config("prod", transport_type="python")
                 .with_args({"env": {"API_KEY": "secret"}})
                 .init())
        
        config.save()  # Persist
    """
    
    def __init__(self, name: str, transport_type: TransportType = "stdio"):
        self.name = name
        self.transport_type = transport_type
        self._env: Dict[str, str] = {}
        self._env_vars: Dict[str, str] = {}
        self._cwd: str | None = None
        self._args: list[str] = []
        self._keep_alive: bool = True
        self._log_file: str | None = None
        self._python_cmd: str | None = None
        self._python_version: str | None = None
        self._with_packages: list[str] = []
        self._pending_env_key: str | None = None
    
    def add_env(self, key: str) -> "ConfigBuilder":
        """
        Add environment variable (call .with_value() next).
        
        Automatically uses env or env_vars based on transport_type.
        
        Args:
            key: Environment variable name
        
        Returns:
            Self for chaining
        """
        self._pending_env_key = key
        return self
    
    def with_value(self, value: str) -> "ConfigBuilder":
        """
        Set value for pending environment variable.
        
        Args:
            value: Environment variable value
        
        Returns:
            Self for chaining
        """
        if self._pending_env_key is None:
            raise ValueError("Call add_env() before with_value()")
        
        # Use correct dict based on transport type
        if self.transport_type in ["npx", "uv", "uvx"]:
            self._env_vars[self._pending_env_key] = value
        else:
            self._env[self._pending_env_key] = value
        
        self._pending_env_key = None
        return self
    
    def with_args(self, args: dict[str, Any]) -> "ConfigBuilder":
        """
        Set configuration from dictionary.
        
        Args:
            args: Dict with env/env_vars, cwd, args, keep_alive, log_file, etc.
        
        Returns:
            Self for chaining
        """
        if "env" in args:
            self._env.update(args["env"])
        if "env_vars" in args:
            self._env_vars.update(args["env_vars"])
        if "cwd" in args:
            self._cwd = args["cwd"]
        if "args" in args:
            self._args = args["args"]
        if "keep_alive" in args:
            self._keep_alive = args["keep_alive"]
        if "log_file" in args:
            self._log_file = args["log_file"]
        if "python_cmd" in args:
            self._python_cmd = args["python_cmd"]
        if "python_version" in args:
            self._python_version = args["python_version"]
        if "with_packages" in args:
            self._with_packages = args["with_packages"]
        
        return self
    
    def cwd(self, path: str) -> "ConfigBuilder":
        """Set working directory."""
        self._cwd = path
        return self
    
    def keep_alive(self, enabled: bool) -> "ConfigBuilder":
        """Set keep_alive flag."""
        self._keep_alive = enabled
        return self
    
    def log_file(self, path: str) -> "ConfigBuilder":
        """Set log file path."""
        self._log_file = path
        return self
    
    def python_cmd(self, cmd: str) -> "ConfigBuilder":
        """Set Python executable path (python transport only)."""
        if self.transport_type != "python":
            raise ValueError("python_cmd only valid for transport_type='python'")
        self._python_cmd = cmd
        return self
    
    def python_version(self, version: str) -> "ConfigBuilder":
        """Set Python version (uv/uvx transports only)."""
        if self.transport_type not in ["uv", "uvx"]:
            raise ValueError("python_version only valid for transport_type='uv' or 'uvx'")
        self._python_version = version
        return self
    
    def with_packages(self, packages: list[str]) -> "ConfigBuilder":
        """Set additional packages (uv/uvx transports only)."""
        if self.transport_type not in ["uv", "uvx"]:
            raise ValueError("with_packages only valid for transport_type='uv' or 'uvx'")
        self._with_packages = packages
        return self
    
    def init(self) -> StdioConfig:
        """
        Compile and validate configuration.
        
        Returns:
            StdioConfig object ready to save or use
        
        Raises:
            ValueError: If pending env var has no value
        """
        if self._pending_env_key is not None:
            raise ValueError(f"Pending env var '{self._pending_env_key}' has no value")
        
        return StdioConfig(
            name=self.name,
            transport_type=self.transport_type,
            env=self._env,
            env_vars=self._env_vars,
            cwd=self._cwd,
            args=self._args,
            keep_alive=self._keep_alive,
            log_file=self._log_file,
            python_cmd=self._python_cmd,
            python_version=self._python_version,
            with_packages=self._with_packages
        )


def create_config(name: str, transport_type: TransportType = "stdio") -> ConfigBuilder:
    """
    Create a new configuration builder.
    
    Args:
        name: Configuration name
        transport_type: Transport type (determines which options are valid)
    
    Returns:
        ConfigBuilder for fluent configuration
    
    Example:
        # Python transport
        config = (create_config("prod", transport_type="python")
                 .add_env("API_KEY").with_value("secret")
                 .python_cmd("/usr/bin/python3.11")
                 .init())
        
        # NPX transport (uses env_vars)
        config = (create_config("npx-config", transport_type="npx")
                 .add_env("API_KEY").with_value("secret")  # Automatically uses env_vars
                 .init())
    """
    return ConfigBuilder(name, transport_type)


def load_config(name: str) -> StdioConfig:
    """
    Load saved configuration from disk.
    
    Args:
        name: Configuration name
    
    Returns:
        StdioConfig object
    
    Example:
        config = load_config("production")
        server = load_server("python server.py").with_config(config)
    """
    return StdioConfig.load(name)


__all__ = ["create_config", "load_config", "StdioConfig", "ConfigBuilder", "TransportType"]
