"""Utility functions for formatting and helpers."""

import json
from typing import Any
from .models import Task


# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BRIGHT_BLUE = "\033[94m"


def colorize(text: str, color: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{color}{text}{RESET}"


def bold(text: str) -> str:
    """Make text bold."""
    return f"{BOLD}{text}{RESET}"


def dim(text: str) -> str:
    """Make text dim."""
    return f"{DIM}{text}{RESET}"


def format_json(data: Any) -> str:
    """Format data as pretty JSON."""
    return json.dumps(data, indent=2)


def print_json(data: Any) -> None:
    """Print data as JSON."""
    print(format_json(data))


def format_priority(priority: int) -> str:
    """Format priority as P0-P4."""
    return f"P{priority}"


def parse_priority(value: str) -> int:
    """Parse priority from string (accepts 0-4 or P0-P4)."""
    value = value.upper().strip()
    if value.startswith("P"):
        value = value[1:]
    try:
        priority = int(value)
        if 0 <= priority <= 4:
            return priority
    except ValueError:
        pass
    raise ValueError(f"Invalid priority: {value}. Must be 0-4 or P0-P4")


def format_table(tasks: list[Task]) -> None:
    """Display tasks in condensed format with Unicode icons."""
    if not tasks:
        print(colorize("No tasks found", YELLOW))
        return

    # Status icons with colors
    STATUS_ICONS = {
        "open": ("○", YELLOW),
        "in_progress": ("◐", BLUE),
        "to_review": ("◑", MAGENTA),
        "closed": ("✓", GREEN)
    }

    # Priority colors
    PRIORITY_COLORS = {
        0: RED,
        1: YELLOW,
        2: WHITE,
        3: DIM,
        4: DIM
    }

    for task in tasks:
        # Get status icon and color
        icon, status_color = STATUS_ICONS.get(task.status, ("?", WHITE))
        colored_icon = colorize(icon, status_color)

        # Get priority with color
        priority_text = format_priority(task.priority)
        priority_color = PRIORITY_COLORS.get(task.priority, WHITE)
        colored_priority = colorize(priority_text, priority_color)

        # ID in bright blue
        colored_id = colorize(task.id, BRIGHT_BLUE)

        # Type in dim
        type_text = f"[{task.type}]"
        colored_type = dim(type_text)

        # Format: <icon> <id> <priority> <title> [<type>]
        print(f"{colored_icon} {colored_id} {colored_priority} {task.title} {colored_type}")


def format_task_detail(task: Task) -> None:
    """Display detailed task information."""
    print(f"\n{colorize(task.id, CYAN)}{bold(':')}{bold(' ')}{bold(task.title)}")
    print(dim(f"Created: {task.created_at}"))
    print(dim(f"Updated: {task.updated_at}"))
    if task.closed_at:
        print(dim(f"Closed: {task.closed_at}"))

    print(f"\nType:     {task.type}")
    status_color = _status_color_code(task.status)
    print(f"Status:   {colorize(task.status, status_color)}")
    print(f"Priority: {format_priority(task.priority)}")
    print(f"Assignee: {task.assignee or '-'}")

    if task.labels:
        print(f"Labels:   {', '.join(task.labels)}")

    if task.description:
        print(f"\n{bold('Description:')}\n{task.description}")

    if task.notes:
        print(f"\n{bold('Notes:')}\n{task.notes}")

    if task.dependencies:
        print(f"\n{bold('Dependencies:')}")
        for dep_id in task.dependencies:
            print(f"  - {dep_id}")

    print()


def _status_color_code(status: str) -> str:
    """Get ANSI color code for status."""
    return {
        "open": YELLOW,
        "in_progress": BLUE,
        "to_review": MAGENTA,
        "closed": GREEN
    }.get(status, WHITE)
