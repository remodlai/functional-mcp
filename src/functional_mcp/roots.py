"""
Roots management for MCP servers.

Handles directory roots that filesystem servers should focus on.
"""

from pathlib import Path


def normalize_roots(roots: str | list[str] | Path | list[Path] | None) -> list[str]:
    """
    Normalize roots to list of strings.
    
    Args:
        roots: Single root, list of roots, or None
    
    Returns:
        List of root paths as strings
    
    Example:
        >>> normalize_roots("/tmp")
        ['/tmp']
        >>> normalize_roots(["/tmp", "/home"])
        ['/tmp', '/home']
        >>> normalize_roots(Path("/tmp"))
        ['/tmp']
    """
    if roots is None:
        return []
    
    if isinstance(roots, (str, Path)):
        roots = [roots]
    
    return [str(Path(r).resolve()) for r in roots]


__all__ = ["normalize_roots"]

