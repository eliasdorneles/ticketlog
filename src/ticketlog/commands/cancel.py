"""Cancel command implementation."""

from ..storage import Storage
from ..config import Config
from ..utils import print_json, colorize, RED, GREEN, YELLOW


def cancel_tasks(args) -> None:
    """Cancel one or more tasks."""
    config = Config.load()
    storage = Storage(config=config)
    canceled = []

    # Validate mutually exclusive options
    if args.review and args.ids:
        print(colorize("Error: Cannot specify both --review and specific task IDs", RED))
        return

    if not args.review and not args.ids:
        print(colorize("Error: Must specify either --review or at least one task ID", RED))
        return

    # Build cancel note
    if args.reason:
        cancel_note = f"Canceled, with reason: {args.reason}"
    else:
        cancel_note = "Canceled"

    # Determine which tasks to cancel
    if args.review:
        # Get all tasks in to_review status
        all_tasks = storage.get_all_tasks()
        tasks_to_cancel = [t for t in all_tasks if t.status == "to_review"]
        
        if not tasks_to_cancel:
            print(colorize("No tasks found in to_review status", YELLOW))
            return
    else:
        # Cancel specific tasks by ID
        tasks_to_cancel = []
        for task_id in args.ids:
            task = storage.get_task_by_id(task_id)
            if not task:
                print(colorize(f"Error: Task {task_id} not found", RED))
                continue
            tasks_to_cancel.append(task)

    # Cancel the tasks
    for task in tasks_to_cancel:
        # Append cancel note to existing notes
        if task.notes:
            new_notes = f"{task.notes}\n{cancel_note}"
        else:
            new_notes = cancel_note
        
        updated_task = task.update_fields(status="closed", notes=new_notes)
        storage.save_task(updated_task)
        canceled.append(updated_task)

    # Output
    if args.json:
        print_json([t.to_dict() for t in canceled])
    else:
        if len(canceled) == 1:
            print(colorize(f"Canceled task {canceled[0].id}", GREEN))
        elif canceled:
            print(colorize(f"Canceled {len(canceled)} tasks", GREEN))
