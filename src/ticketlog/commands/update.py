"""Update command implementation."""

from ..storage import Storage
from ..utils import print_json, parse_priority, colorize, RED, GREEN


def update_task(args) -> None:
    """Update a task."""
    storage = Storage()
    task = storage.get_task_by_id(args.id)

    if not task:
        print(colorize(f"Error: Task {args.id} not found", RED))
        return

    # Build update dict
    updates = {}

    if args.title is not None:
        updates["title"] = args.title

    if args.description is not None:
        updates["description"] = args.description

    if args.status is not None:
        updates["status"] = args.status

    if args.type is not None:
        updates["type"] = args.type

    if args.priority is not None:
        updates["priority"] = parse_priority(str(args.priority))

    if args.assignee is not None:
        updates["assignee"] = args.assignee

    if args.notes is not None:
        updates["notes"] = args.notes

    # Handle labels
    if args.add_label:
        new_labels = set(task.labels)
        for label in args.add_label:
            new_labels.add(label)
        updates["labels"] = list(new_labels)

    if args.remove_label:
        new_labels = set(task.labels)
        for label in args.remove_label:
            new_labels.discard(label)
        updates["labels"] = list(new_labels)

    # Apply updates
    updated_task = task.update_fields(**updates)

    # Save
    storage.save_task(updated_task)

    # Output
    if args.json:
        print_json(updated_task.to_dict())
    else:
        print(colorize(f"Updated task {updated_task.id}", GREEN))
