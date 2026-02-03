"""Dependency command implementation."""

from ..storage import Storage
from ..utils import print_json, colorize, bold, dim, RED, GREEN, YELLOW, CYAN


def detect_cycle(task_id: str, depends_on: str, all_tasks: list) -> bool:
    """Detect if adding this dependency would create a cycle."""
    # Build dependency graph
    deps = {t.id: set(t.dependencies) for t in all_tasks}

    # Add the new dependency
    if task_id not in deps:
        deps[task_id] = set()
    deps[task_id].add(depends_on)

    # DFS to detect cycle
    visited = set()
    rec_stack = set()

    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in deps.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    return has_cycle(task_id)


def add_dependency(args) -> None:
    """Add a dependency between tasks."""
    storage = Storage()

    task = storage.get_task_by_id(args.task_id)
    depends_on = storage.get_task_by_id(args.depends_on_id)

    if not task:
        print(colorize(f"Error: Task {args.task_id} not found", RED))
        return

    if not depends_on:
        print(colorize(f"Error: Task {args.depends_on_id} not found", RED))
        return

    # Check for cycles
    all_tasks = storage.get_all_tasks()
    if detect_cycle(args.task_id, args.depends_on_id, all_tasks):
        print(colorize("Error: Adding this dependency would create a cycle", RED))
        return

    # Add dependency if not already present
    if args.depends_on_id not in task.dependencies:
        new_deps = task.dependencies + [args.depends_on_id]
        updated_task = task.update_fields(dependencies=new_deps)
        storage.save_task(updated_task)

        if args.json:
            print_json(updated_task.to_dict())
        else:
            print(colorize(f"Added dependency: {args.task_id} depends on {args.depends_on_id}", GREEN))
    else:
        print(colorize("Dependency already exists", YELLOW))


def remove_dependency(args) -> None:
    """Remove a dependency between tasks."""
    storage = Storage()
    task = storage.get_task_by_id(args.task_id)

    if not task:
        print(colorize(f"Error: Task {args.task_id} not found", RED))
        return

    # Remove dependency
    if args.depends_on_id in task.dependencies:
        new_deps = [d for d in task.dependencies if d != args.depends_on_id]
        updated_task = task.update_fields(dependencies=new_deps)
        storage.save_task(updated_task)

        if args.json:
            print_json(updated_task.to_dict())
        else:
            print(colorize(f"Removed dependency: {args.task_id} no longer depends on {args.depends_on_id}", GREEN))
    else:
        print(colorize("Dependency does not exist", YELLOW))


def list_dependencies(args) -> None:
    """List dependencies for a task."""
    storage = Storage()
    task = storage.get_task_by_id(args.task_id)

    if not task:
        print(colorize(f"Error: Task {args.task_id} not found", RED))
        return

    # Find tasks that depend on this task (blocked by this)
    all_tasks = storage.get_all_tasks()
    blocked_by_this = [t for t in all_tasks if task.id in t.dependencies]

    if args.json:
        output = {
            "task_id": task.id,
            "depends_on": task.dependencies,
            "blocks": [t.id for t in blocked_by_this]
        }
        print_json(output)
    else:
        print(f"\n{bold(f'Dependencies for {task.id}:')}")

        if task.dependencies:
            print(f"\n{colorize('Depends on (blocks this task):', CYAN)}")
            for dep_id in task.dependencies:
                dep_task = storage.get_task_by_id(dep_id)
                if dep_task:
                    print(f"  - {dep_id}: {dep_task.title} [{dep_task.status}]")
                else:
                    print(f"  - {dep_id}: {colorize('(not found)', RED)}")
        else:
            print(f"\n{dim('No dependencies')}")

        if blocked_by_this:
            print(f"\n{colorize('Blocks these tasks:', CYAN)}")
            for blocked_task in blocked_by_this:
                print(f"  - {blocked_task.id}: {blocked_task.title} [{blocked_task.status}]")
        else:
            print(f"\n{dim('Does not block any tasks')}")

        print()
