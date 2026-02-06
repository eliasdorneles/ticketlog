"""List command implementation."""

from ..storage import Storage
from ..config import Config
from ..utils import format_table, print_json


def list_tasks(args) -> None:
    """List tasks with optional filtering."""
    config = Config.load()
    storage = Storage(config=config)
    tasks = storage.get_all_tasks()

    # Apply filters
    if args.status:
        tasks = [t for t in tasks if t.status == args.status]
    elif not args.all:
        # Default: show open and in_progress tasks
        tasks = [t for t in tasks if t.status in ("open", "in_progress")]

    if args.type:
        tasks = [t for t in tasks if t.type == args.type]

    if args.assignee:
        tasks = [t for t in tasks if t.assignee == args.assignee]

    if args.label:
        tasks = [t for t in tasks if args.label in t.labels]

    # Sort by priority (0 first), then by ID
    tasks.sort(key=lambda t: (t.priority, t.id))

    # Output
    if args.json:
        print_json([t.to_dict() for t in tasks])
    else:
        format_table(tasks)
