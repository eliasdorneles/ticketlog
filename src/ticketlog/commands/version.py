"""Version command for ticketlog."""

from ticketlog import __version__


def show_version(args):
    """Display the current version of ticketlog."""
    if args.json:
        import json
        print(json.dumps({"version": __version__}))
    else:
        print(f"ticketlog {__version__}")
