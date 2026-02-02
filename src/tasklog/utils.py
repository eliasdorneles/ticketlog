"""Utility functions for formatting and helpers."""

import json
from typing import Any
from rich.console import Console
from rich.table import Table
from .models import Task


console = Console()


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
    """Display tasks as a formatted table."""
    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="bright_blue", width=8)
    table.add_column("Title", style="white", min_width=20, no_wrap=False)
    table.add_column("Type", width=8)
    table.add_column("Status", width=12)
    table.add_column("Priority", width=8)
    table.add_column("Assignee", width=12)
    table.add_column("Labels", width=15)

    for task in tasks:
        # Color code status
        status_color = {
            "open": "yellow",
            "in_progress": "blue",
            "to_review": "magenta",
            "closed": "green"
        }.get(task.status, "white")

        # Color code priority
        priority_color = {
            0: "red",
            1: "yellow",
            2: "white",
            3: "dim",
            4: "dim"
        }.get(task.priority, "white")

        table.add_row(
            task.id,
            task.title,
            task.type,
            f"[{status_color}]{task.status}[/{status_color}]",
            f"[{priority_color}]{format_priority(task.priority)}[/{priority_color}]",
            task.assignee or "-",
            ", ".join(task.labels) if task.labels else "-"
        )

    console.print(table)


def format_task_detail(task: Task) -> None:
    """Display detailed task information."""
    console.print(f"\n[bold cyan]{task.id}[/bold cyan]: [bold]{task.title}[/bold]")
    console.print(f"[dim]Created: {task.created_at}[/dim]")
    console.print(f"[dim]Updated: {task.updated_at}[/dim]")
    if task.closed_at:
        console.print(f"[dim]Closed: {task.closed_at}[/dim]")

    console.print(f"\nType:     {task.type}")
    console.print(f"Status:   [{_status_color(task.status)}]{task.status}[/{_status_color(task.status)}]")
    console.print(f"Priority: {format_priority(task.priority)}")
    console.print(f"Assignee: {task.assignee or '-'}")

    if task.labels:
        console.print(f"Labels:   {', '.join(task.labels)}")

    if task.description:
        console.print(f"\n[bold]Description:[/bold]\n{task.description}")

    if task.notes:
        console.print(f"\n[bold]Notes:[/bold]\n{task.notes}")

    if task.dependencies:
        console.print(f"\n[bold]Dependencies:[/bold]")
        for dep_id in task.dependencies:
            console.print(f"  - {dep_id}")

    console.print()


def _status_color(status: str) -> str:
    """Get color for status."""
    return {
        "open": "yellow",
        "in_progress": "blue",
        "to_review": "magenta",
        "closed": "green"
    }.get(status, "white")
