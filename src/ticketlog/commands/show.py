"""Show command implementation."""

from ..storage import Storage
from ..config import Config
from ..utils import format_task_detail, print_json, colorize, RED


def show_task(args) -> None:
    """Show detailed task information."""
    config = Config.load()
    storage = Storage(config=config)
    task = storage.get_task_by_id(args.id)

    if not task:
        print(colorize(f"Error: Task {args.id} not found", RED))
        return

    # Output
    if args.json:
        print_json(task.to_dict())
    else:
        storage.check_dead_history()
        format_task_detail(task)
