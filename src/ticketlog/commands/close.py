"""Close command implementation."""

from ..storage import Storage
from ..config import Config
from ..utils import print_json, colorize, RED, GREEN, YELLOW


def close_tasks(args) -> None:
    """Close one or more tasks."""
    config = Config.load()
    storage = Storage(config=config)
    closed = []

    # Validate mutually exclusive options
    if args.review and args.ids:
        print(colorize("Error: Cannot specify both --review and specific task IDs", RED))
        return

    if not args.review and not args.ids:
        print(colorize("Error: Must specify either --review or at least one task ID", RED))
        return

    # Determine which tasks to close
    if args.review:
        # Get all tasks in to_review status
        all_tasks = storage.get_all_tasks()
        tasks_to_close = [t for t in all_tasks if t.status == "to_review"]
        
        if not tasks_to_close:
            print(colorize("No tasks found in to_review status", YELLOW))
            return
    else:
        # Close specific tasks by ID
        tasks_to_close = []
        for task_id in args.ids:
            task = storage.get_task_by_id(task_id)
            if not task:
                print(colorize(f"Error: Task {task_id} not found", RED))
                continue
            tasks_to_close.append(task)

    # Close the tasks
    for task in tasks_to_close:
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
