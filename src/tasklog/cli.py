"""Command-line interface for tasklog."""

import argparse
import sys
from .commands.create import create_task
from .commands.list import list_tasks
from .commands.show import show_task
from .commands.update import update_task
from .commands.close import close_tasks
from .commands.ready import ready_tasks
from .commands.dep import add_dependency, remove_dependency, list_dependencies


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lightweight task/issue tracking tool",
        prog="tl"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("title", help="Task title")
    create_parser.add_argument("--type", default="task", choices=["task", "bug", "feature", "epic", "chore"],
                              help="Task type (default: task)")
    create_parser.add_argument("--priority", type=str, default="2",
                              help="Priority: 0-4 or P0-P4 (default: 2/P2)")
    create_parser.add_argument("--description", help="Task description")
    create_parser.add_argument("--assignee", help="Assignee username")
    create_parser.add_argument("--labels", help="Comma-separated labels")
    create_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", choices=["open", "in_progress", "to_review", "closed"],
                            help="Filter by status")
    list_parser.add_argument("--type", choices=["task", "bug", "feature", "epic", "chore"],
                            help="Filter by type")
    list_parser.add_argument("--assignee", help="Filter by assignee")
    list_parser.add_argument("--label", help="Filter by label")
    list_parser.add_argument("--all", action="store_true",
                            help="Show all tasks (default: only open and in_progress)")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show task details")
    show_parser.add_argument("id", help="Task ID")
    show_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("id", help="Task ID")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--description", help="New description")
    update_parser.add_argument("--status", choices=["open", "in_progress", "to_review", "closed"],
                              help="New status")
    update_parser.add_argument("--type", choices=["task", "bug", "feature", "epic", "chore"],
                              help="New type")
    update_parser.add_argument("--priority", type=str, help="New priority (0-4 or P0-P4)")
    update_parser.add_argument("--assignee", help="New assignee")
    update_parser.add_argument("--notes", help="New notes")
    update_parser.add_argument("--add-label", action="append", help="Add label (can be used multiple times)")
    update_parser.add_argument("--remove-label", action="append", help="Remove label (can be used multiple times)")
    update_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Close command
    close_parser = subparsers.add_parser("close", help="Close one or more tasks")
    close_parser.add_argument("ids", nargs="+", help="Task ID(s) to close")
    close_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Ready command
    ready_parser = subparsers.add_parser("ready", help="Show tasks ready to work on")
    ready_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Dependency commands
    dep_parser = subparsers.add_parser("dep", help="Manage task dependencies")
    dep_subparsers = dep_parser.add_subparsers(dest="dep_command", help="Dependency commands")

    # dep add
    dep_add_parser = dep_subparsers.add_parser("add", help="Add a dependency")
    dep_add_parser.add_argument("task_id", help="Task ID that will depend on another task")
    dep_add_parser.add_argument("depends_on_id", help="Task ID that blocks the first task")
    dep_add_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # dep remove
    dep_remove_parser = dep_subparsers.add_parser("remove", help="Remove a dependency")
    dep_remove_parser.add_argument("task_id", help="Task ID")
    dep_remove_parser.add_argument("depends_on_id", help="Dependency to remove")
    dep_remove_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # dep list
    dep_list_parser = dep_subparsers.add_parser("list", help="List dependencies for a task")
    dep_list_parser.add_argument("task_id", help="Task ID")
    dep_list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to appropriate command
    try:
        if args.command == "create":
            create_task(args)
        elif args.command == "list":
            list_tasks(args)
        elif args.command == "show":
            show_task(args)
        elif args.command == "update":
            update_task(args)
        elif args.command == "close":
            close_tasks(args)
        elif args.command == "ready":
            ready_tasks(args)
        elif args.command == "dep":
            if not args.dep_command:
                dep_parser.print_help()
                sys.exit(1)
            if args.dep_command == "add":
                add_dependency(args)
            elif args.dep_command == "remove":
                remove_dependency(args)
            elif args.dep_command == "list":
                list_dependencies(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
