"""Start command implementation."""

from ..storage import Storage
from ..config import Config
from ..utils import print_json, colorize, RED, GREEN


def start_task(args) -> None:
    """Start working on a task (set status to in_progress)."""
    config = Config.load()
    storage = Storage(config=config)
    task = storage.get_task_by_id(args.id)

    if not task:
        print(colorize(f"Error: Task {args.id} not found", RED))
        return

    # Build update dict
    updates = {"status": "in_progress"}

    # Optionally assign to someone
    if args.assignee is not None:
        updates["assignee"] = args.assignee

    # Apply updates
    updated_task = task.update_fields(**updates)

    # Save
    storage.save_task(updated_task)

    # Output
    if args.json:
        print_json(updated_task.to_dict())
    else:
        storage.check_dead_history()
        msg = f"Started task {updated_task.id}"
        if args.assignee:
            msg += f" (assigned to {args.assignee})"
        print(colorize(msg, GREEN))
