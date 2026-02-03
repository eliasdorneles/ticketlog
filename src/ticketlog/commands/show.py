"""Show command implementation."""

from ..storage import Storage
from ..utils import format_task_detail, print_json, colorize, RED


def show_task(args) -> None:
    """Show detailed task information."""
    storage = Storage()
    task = storage.get_task_by_id(args.id)

    if not task:
        print(colorize(f"Error: Task {args.id} not found", RED))
        return

    # Output
    if args.json:
        print_json(task.to_dict())
    else:
        format_task_detail(task)
