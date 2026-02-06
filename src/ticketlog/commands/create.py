"""Create command implementation."""

from ..models import Task
from ..storage import Storage
from ..config import Config
from ..utils import print_json, parse_priority, colorize, GREEN


def create_task(args) -> None:
    """Create a new task."""
    config = Config.load()
    storage = Storage(config=config)

    # Parse labels if provided
    labels = []
    if args.labels:
        labels = [label.strip() for label in args.labels.split(",")]

    # Parse priority
    priority = args.priority
    if args.priority is not None:
        priority = parse_priority(str(args.priority))

    # Create task
    task_id = storage.get_next_id()
    task = Task.create(
        id=task_id,
        title=args.title,
        description=args.description or "",
        type=args.type,
        priority=priority,
        assignee=args.assignee,
        labels=labels,
    )

    # Save task
    storage.save_task(task)

    # Output
    if args.json:
        print_json(task.to_dict())
    else:
        print(colorize(f"Created task {task.id}", GREEN))
