"""Ready command implementation."""

from ..storage import Storage
from ..config import Config
from ..utils import format_table, print_json


def ready_tasks(args) -> None:
    """Show tasks ready to work on (no unresolved dependencies)."""
    config = Config.load()
    storage = Storage(config=config)
    all_tasks = storage.get_all_tasks()

    # Build a set of closed task IDs
    closed_ids = {t.id for t in all_tasks if t.status == "closed"}

    # Filter for tasks with status=open and all dependencies closed
    ready = []
    for task in all_tasks:
        if task.status != "open":
            continue

        # Check if all dependencies are closed
        if all(dep_id in closed_ids for dep_id in task.dependencies):
            ready.append(task)

    # Sort by priority (0 first), then by ID
    ready.sort(key=lambda t: (t.priority, t.id))

    # Output
    if args.json:
        print_json([t.to_dict() for t in ready])
    else:
        storage.check_dead_history()
        format_table(ready)
