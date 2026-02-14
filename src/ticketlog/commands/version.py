"""Version command for ticketlog."""

import json

from ticketlog import __version__


def show_version(args):
    """Display the current version of ticketlog."""
    if args.json:
        print(json.dumps({"version": __version__}))
    else:
        print(f"ticketlog {__version__}")
