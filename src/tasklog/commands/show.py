"""Show command implementation."""

from ..storage import Storage
from ..utils import format_task_detail, print_json, console


def show_task(args) -> None:
    """Show detailed task information."""
    storage = Storage()
    task = storage.get_task_by_id(args.id)

    if not task:
        console.print(f"[red]Error: Task {args.id} not found[/red]")
        return

    # Output
    if args.json:
        print_json(task.to_dict())
    else:
        format_task_detail(task)
