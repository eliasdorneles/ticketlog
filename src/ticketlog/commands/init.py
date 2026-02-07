"""Initialize .ticketlog.toml configuration file."""

import re
import sys
from pathlib import Path
from typing import Optional

from ..config import find_git_root
from ..utils import colorize, print_json, GREEN, RED


# TOML template for configuration file
TOML_TEMPLATE = """# Ticketlog Configuration
# https://github.com/eliasdorneles/ticketlog

[project]
# Prefix for ticket IDs (auto-generated from directory name)
# New tickets will have format: {{prefix}}-{{3-letter-random-id}}
# Example: myc-a3f, tic-x9k
prefix = "{prefix}"

# Warn when dead history exceeds this ratio (0.0 to 1.0)
# dead_history_threshold = 0.3
"""


def derive_prefix_from_directory(directory: Path) -> str:
    """Derive a 3-letter prefix from directory name.

    Rules:
    - Strip non-alphanumeric characters
    - Take first 3 letters
    - Convert to lowercase
    - Fallback to "tl" if less than 3 characters available

    Examples:
        "my-cool-project" -> "myc"
        "ticketlog" -> "tic"
        "FooBar" -> "foo"
        "MyApp" -> "mya"
        "ab" -> "tl" (fallback)
    """
    name = directory.name

    # Keep only alphanumeric characters
    name = re.sub(r'[^a-zA-Z0-9]+', '', name)

    # Convert to lowercase
    name = name.lower()

    # Take first 3 characters
    if len(name) >= 3:
        return name[:3]

    # Fallback if less than 3 characters
    return "tl"


def init_config(args):
    """Initialize .ticketlog.toml configuration file.

    Args:
        args: Command-line arguments containing:
            - prefix: Optional custom prefix (overrides auto-generation)
            - force: Whether to overwrite existing file
            - json: Whether to output as JSON
    """
    # Determine target directory (git root or current directory)
    git_root = find_git_root(Path.cwd())
    target_dir = git_root if git_root else Path.cwd()
    target_path = target_dir / ".ticketlog.toml"

    # Check if file exists
    if target_path.exists() and not args.force:
        if args.json:
            print_json({
                "success": False,
                "error": "Configuration file already exists",
                "path": str(target_path)
            })
        else:
            print(colorize(f"Error: Configuration file already exists at {target_path}", RED))
            print(colorize("Use --force to overwrite.", RED))
        sys.exit(1)

    # Determine prefix (custom or auto-generated)
    if args.prefix:
        prefix = args.prefix
    else:
        prefix = derive_prefix_from_directory(target_dir)

    # Generate TOML content
    toml_content = TOML_TEMPLATE.format(prefix=prefix)

    # Write file
    try:
        target_path.write_text(toml_content)
    except OSError as e:
        if args.json:
            print_json({
                "success": False,
                "error": f"Cannot write to {target_path}: {e}",
                "path": str(target_path)
            })
        else:
            print(colorize(f"Error: Cannot write to {target_path}: {e}", RED))
        sys.exit(1)

    # Output success message
    if args.json:
        print_json({
            "success": True,
            "path": str(target_path),
            "prefix": prefix
        })
    else:
        print(colorize(f"Created configuration at {target_path} with prefix \"{prefix}\"", GREEN))
