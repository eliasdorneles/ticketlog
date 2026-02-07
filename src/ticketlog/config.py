"""Configuration management for ticketlog."""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Python 3.11+ has tomllib, fallback to tomli for 3.10
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@dataclass
class Config:
    """Configuration settings for ticketlog."""

    prefix: str = "tl"
    dead_history_threshold: float = 0.3

    @classmethod
    def load(cls, start_path: Optional[Path] = None) -> "Config":
        """Load config from .ticketlog.toml, walking up directory tree.

        Args:
            start_path: Starting directory (defaults to cwd)

        Returns:
            Config instance with loaded or default settings
        """
        if start_path is None:
            start_path = Path.cwd()

        # Walk up directory tree
        current = start_path.resolve()
        git_root = find_git_root(current)

        while True:
            config_file = current / ".ticketlog.toml"
            if config_file.exists():
                return cls.from_file(config_file)

            # Stop at git root or filesystem root
            if current == current.parent or (git_root and current == git_root):
                break
            current = current.parent

        return cls()  # Return defaults

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load config from TOML file.

        Args:
            path: Path to .ticketlog.toml file

        Returns:
            Config instance with loaded settings

        Raises:
            RuntimeError: If TOML support is not available
        """
        if tomllib is None:
            raise RuntimeError(
                "TOML support requires Python 3.11+ or the 'tomli' package. "
                "Install with: uv add tomli"
            )

        with open(path, "rb") as f:
            data = tomllib.load(f)

        project_config = data.get("project", {})
        return cls(
            prefix=project_config.get("prefix", "tl"),
            dead_history_threshold=project_config.get("dead_history_threshold", 0.3),
        )


def find_git_root(path: Path) -> Optional[Path]:
    """Find git root directory.

    Args:
        path: Starting directory

    Returns:
        Git root path or None if not in a git repo
    """
    current = path.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return None
