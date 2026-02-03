"""Close command implementation."""

from ..storage import Storage
from ..utils import print_json, colorize, RED, GREEN


def close_tasks(args) -> None:
    """Close one or more tasks."""
    storage = Storage()
    closed = []

    for task_id in args.ids:
        task = storage.get_task_by_id(task_id)

        if not task:
            print(colorize(f"Error: Task {task_id} not found", RED))
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
            print(colorize(f"Closed task {closed[0].id}", GREEN))
        elif closed:
            print(colorize(f"Closed {len(closed)} tasks", GREEN))
