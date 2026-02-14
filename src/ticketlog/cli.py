"""Command-line interface for ticketlog."""

import argparse
import sys
from . import __version__
from .commands.create import create_task
from .commands.list import list_tasks
from .commands.show import show_task
from .commands.update import update_task
from .commands.close import close_tasks
from .commands.cancel import cancel_tasks
from .commands.ready import ready_tasks
from .commands.clean import clean_log
from .commands.dep import add_dependency, remove_dependency, list_dependencies
from .commands.import_beads import import_from_beads
from .commands.start import start_task
from .commands.init import init_config
from .commands.version import show_version


# Status shortcuts mapping
STATUS_SHORTCUTS = {
    'o': 'open',
    'open': 'open',
    'ip': 'in_progress',
    'wip': 'in_progress',
    'progress': 'in_progress',
    'in_progress': 'in_progress',
    'tr': 'to_review',
    'review': 'to_review',
    'to_review': 'to_review',
    'c': 'closed',
    'closed': 'closed',
    'done': 'closed',
}

# Type shortcuts mapping
TYPE_SHORTCUTS = {
    't': 'task',
    'task': 'task',
    'b': 'bug',
    'bug': 'bug',
    'f': 'feature',
    'feat': 'feature',
    'feature': 'feature',
    'e': 'epic',
    'epic': 'epic',
    'c': 'chore',
    'chore': 'chore',
}


def normalize_status(status):
    """Normalize status shortcuts to full status names."""
    if status is None:
        return None
    return STATUS_SHORTCUTS.get(status.lower(), status)


def normalize_type(type_val):
    """Normalize type shortcuts to full type names."""
    if type_val is None:
        return None
    return TYPE_SHORTCUTS.get(type_val.lower(), type_val)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lightweight task/issue tracking tool",
        prog="tl"
    )
    parser.add_argument("--version", action="store_true", help="Show version number")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command (aliases: new, add)
    create_parser = subparsers.add_parser("create", aliases=["new", "add"], help="Create a new task")
    create_parser.add_argument("title", help="Task title")
    create_parser.add_argument("-t", "--type", default="task",
                              help="Task type: task/t, bug/b, feature/f/feat, epic/e, chore/c (default: task)")
    create_parser.add_argument("-p", "--priority", type=str, default="2",
                              help="Priority: 0-4 or P0-P4 (default: 2/P2)")
    create_parser.add_argument("-d", "--description", help="Task description")
    create_parser.add_argument("-a", "--assignee", help="Assignee username")
    create_parser.add_argument("-l", "--labels", help="Comma-separated labels")
    create_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # List command (alias: ls)
    list_parser = subparsers.add_parser("list", aliases=["ls"], help="List tasks")
    list_parser.add_argument("-s", "--status",
                            help="Filter by status: open/o, in_progress/ip/wip, to_review/tr/review, closed/c/done")
    list_parser.add_argument("-t", "--type",
                            help="Filter by type: task/t, bug/b, feature/f/feat, epic/e, chore/c")
    list_parser.add_argument("-a", "--assignee", help="Filter by assignee")
    list_parser.add_argument("-l", "--label", help="Filter by label")
    list_parser.add_argument("-A", "--all", action="store_true",
                            help="Show all tasks (default: only open and in_progress)")
    list_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show task details")
    show_parser.add_argument("id", help="Task ID")
    show_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("id", help="Task ID")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("-d", "--description", help="New description")
    update_parser.add_argument("-s", "--status",
                              help="New status: open/o, in_progress/ip/wip, to_review/tr/review, closed/c/done")
    update_parser.add_argument("-t", "--type",
                              help="New type: task/t, bug/b, feature/f/feat, epic/e, chore/c")
    update_parser.add_argument("-p", "--priority", type=str, help="New priority (0-4 or P0-P4)")
    update_parser.add_argument("-a", "--assignee", help="New assignee")
    update_parser.add_argument("--notes", help="New notes")
    update_parser.add_argument("--add-label", action="append", help="Add label (can be used multiple times)")
    update_parser.add_argument("--remove-label", action="append", help="Remove label (can be used multiple times)")
    update_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Close command (aliases: done, rm)
    close_parser = subparsers.add_parser("close", aliases=["done", "rm"], help="Close one or more tasks")
    close_parser.add_argument("ids", nargs="*", help="Task ID(s) to close")
    close_parser.add_argument("--review", action="store_true", help="Close all tasks in to_review status")
    close_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel one or more tasks (close with cancel note)")
    cancel_parser.add_argument("ids", nargs="+", help="Task ID(s) to cancel")
    cancel_parser.add_argument("--reason", help="Reason for cancellation")
    cancel_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Ready command
    ready_parser = subparsers.add_parser("ready", help="Show tasks ready to work on")
    ready_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start working on a task (set status to in_progress)")
    start_parser.add_argument("id", help="Task ID")
    start_parser.add_argument("-a", "--assignee", help="Assignee username (optional)")
    start_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Dependency commands
    dep_parser = subparsers.add_parser("dep", help="Manage task dependencies")
    dep_subparsers = dep_parser.add_subparsers(dest="dep_command", help="Dependency commands")

    # dep add
    dep_add_parser = dep_subparsers.add_parser("add", help="Add a dependency")
    dep_add_parser.add_argument("task_id", help="Task ID that will depend on another task")
    dep_add_parser.add_argument("depends_on_id", help="Task ID that blocks the first task")
    dep_add_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # dep remove
    dep_remove_parser = dep_subparsers.add_parser("remove", help="Remove a dependency")
    dep_remove_parser.add_argument("task_id", help="Task ID")
    dep_remove_parser.add_argument("depends_on_id", help="Dependency to remove")
    dep_remove_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # dep list
    dep_list_parser = dep_subparsers.add_parser("list", help="List dependencies for a task")
    dep_list_parser.add_argument("task_id", help="Task ID")
    dep_list_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Block command (shortcut for dep add)
    block_parser = subparsers.add_parser("block", help="Add a dependency (task_id depends on blocker_id)")
    block_parser.add_argument("task_id", help="Task ID that will be blocked")
    block_parser.add_argument("blocker_id", help="Task ID that blocks the first task")
    block_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Depends command (alias for block)
    depends_parser = subparsers.add_parser("depends", help="Add a dependency (task_id depends on dependency_id)")
    depends_parser.add_argument("task_id", help="Task ID that depends on another")
    depends_parser.add_argument("dependency_id", help="Task ID that the first task depends on")
    depends_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Unblock command (shortcut for dep remove)
    unblock_parser = subparsers.add_parser("unblock", help="Remove a dependency")
    unblock_parser.add_argument("task_id", help="Task ID")
    unblock_parser.add_argument("blocker_id", help="Dependency to remove")
    unblock_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Deduplicate the log file")
    clean_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import tasks from other formats")
    import_subparsers = import_parser.add_subparsers(dest="import_format", help="Format to import from")

    # import beads
    import_beads_parser = import_subparsers.add_parser("beads", help="Import from beads JsonLines")
    import_beads_parser.add_argument("filepath", help="Path to beads issues.jsonl file")
    import_beads_parser.add_argument("--dry-run", action="store_true",
                                      help="Show what would be imported without writing")
    import_beads_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize .ticketlog.toml configuration file")
    init_parser.add_argument("--prefix", help="Prefix for ticket IDs (default: auto-derived from directory name)")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing configuration file")
    init_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Version command
    version_parser = subparsers.add_parser("version", help="Show version number")
    version_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    # Parse arguments
    args = parser.parse_args()

    # Handle --version flag
    if args.version:
        print(f"ticketlog {__version__}")
        sys.exit(0)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Normalize shortcuts for status and type
    if hasattr(args, 'status') and args.status:
        args.status = normalize_status(args.status)
    if hasattr(args, 'type') and args.type:
        args.type = normalize_type(args.type)

    # Route to appropriate command
    try:
        if args.command in ("create", "new", "add"):
            create_task(args)
        elif args.command in ("list", "ls"):
            list_tasks(args)
        elif args.command == "show":
            show_task(args)
        elif args.command == "update":
            update_task(args)
        elif args.command in ("close", "done", "rm"):
            close_tasks(args)
        elif args.command == "cancel":
            cancel_tasks(args)
        elif args.command == "ready":
            ready_tasks(args)
        elif args.command == "start":
            start_task(args)
        elif args.command == "clean":
            clean_log(args)
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
        elif args.command in ("block", "depends"):
            # Convert to dep add args format
            args.depends_on_id = args.blocker_id if hasattr(args, 'blocker_id') else args.dependency_id
            add_dependency(args)
        elif args.command == "unblock":
            # Convert to dep remove args format
            args.depends_on_id = args.blocker_id
            remove_dependency(args)
        elif args.command == "import":
            if not args.import_format:
                import_parser.print_help()
                sys.exit(1)
            if args.import_format == "beads":
                import_from_beads(args)
        elif args.command == "init":
            init_config(args)
        elif args.command == "version":
            show_version(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
