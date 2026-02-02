"""Close command implementation."""

from ..storage import Storage
from ..utils import print_json, console


def close_tasks(args) -> None:
    """Close one or more tasks."""
    storage = Storage()
    closed = []

    for task_id in args.ids:
        task = storage.get_task_by_id(task_id)

        if not task:
            console.print(f"[red]Error: Task {task_id} not found[/red]")
            continue

        # Update to closed status
        updated_task = task.update_fields(status="closed")
        storage.save_task(updated_task)
        closed.append(updated_task)

    # Output
    if args.json:
        print_json([t.to_dict() for t in closed])
    else:
        if len(closed) == 1:
            console.print(f"[green]Closed task {closed[0].id}[/green]")
        elif closed:
            console.print(f"[green]Closed {len(closed)} tasks[/green]")
