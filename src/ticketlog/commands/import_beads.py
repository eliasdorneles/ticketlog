"""Import command for beads JsonLines format."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from ..config import Config
from ..models import Task
from ..storage import Storage
from ..utils import colorize, print_json, GREEN, YELLOW, RED


def convert_timestamp_to_utc(timestamp_str: str | None) -> str | None:
    """Convert ISO timestamp with timezone to UTC Z format.

    Args:
        timestamp_str: ISO timestamp (e.g., "2024-01-15T10:30:00+01:00")

    Returns:
        UTC timestamp with Z suffix (e.g., "2024-01-15T09:30:00Z") or None
    """
    if not timestamp_str:
        return None

    try:
        # Parse ISO timestamp with timezone
        dt = datetime.fromisoformat(timestamp_str)

        # Convert to UTC
        utc_dt = dt.utctimetuple()
        utc_datetime = datetime(*utc_dt[:6])

        # Format with Z suffix
        return utc_datetime.isoformat() + "Z"
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}") from e


def map_status(beads_status: str) -> tuple[str, bool]:
    """Map beads status to ticketlog status.

    Args:
        beads_status: Status from beads (e.g., "open", "closed", "in_progress")

    Returns:
        Tuple of (mapped_status, has_warning)
    """
    status_map = {
        "open": "open",
        "closed": "closed",
        "in_progress": "in_progress",
        "to_review": "to_review",
    }

    mapped = status_map.get(beads_status.lower())
    if mapped:
        return mapped, False

    # Unknown status - default to open with warning
    return "open", True


def map_type(beads_type: str) -> tuple[str, bool]:
    """Map beads issue_type to ticketlog type.

    Args:
        beads_type: Type from beads (e.g., "bug", "feature", "task")

    Returns:
        Tuple of (mapped_type, has_warning)
    """
    type_map = {
        "task": "task",
        "bug": "bug",
        "feature": "feature",
        "epic": "epic",
        "chore": "chore",
    }

    mapped = type_map.get(beads_type.lower())
    if mapped:
        return mapped, False

    # Unknown type - default to task with warning
    return "task", True


def build_notes(created_by: str | None, close_reason: str | None) -> str:
    """Build notes field from beads metadata.

    Args:
        created_by: Creator name from beads
        close_reason: Close reason from beads

    Returns:
        Formatted notes string
    """
    notes_parts = []

    if created_by:
        notes_parts.append(f"Created by: {created_by}")

    if close_reason:
        notes_parts.append(f"Close reason: {close_reason}")

    return "\n".join(notes_parts)


def convert_beads_task(beads_data: dict) -> tuple[Task, list[str]]:
    """Convert beads task data to ticketlog Task.

    Args:
        beads_data: Dictionary from beads JsonLines

    Returns:
        Tuple of (Task object, list of warnings)

    Raises:
        ValueError: If required fields are missing
    """
    warnings = []

    # Required fields
    task_id = beads_data.get("id")
    title = beads_data.get("title")

    if not task_id:
        raise ValueError("Missing required field: id")
    if not title:
        raise ValueError("Missing required field: title")

    # Map status
    beads_status = beads_data.get("status", "open")
    status, status_warning = map_status(beads_status)
    if status_warning:
        warnings.append(f"Unknown status '{beads_status}', defaulting to 'open'")

    # Map type
    beads_type = beads_data.get("issue_type", "task")
    task_type, type_warning = map_type(beads_type)
    if type_warning:
        warnings.append(f"Unknown type '{beads_type}', defaulting to 'task'")

    # Convert timestamps
    try:
        created_at = convert_timestamp_to_utc(beads_data.get("created_at"))
        updated_at = convert_timestamp_to_utc(beads_data.get("updated_at"))
        closed_at = convert_timestamp_to_utc(beads_data.get("closed_at"))
    except ValueError as e:
        raise ValueError(f"Timestamp conversion failed: {e}") from e

    # Use current time if timestamps missing
    now = datetime.utcnow().isoformat() + "Z"
    if not created_at:
        created_at = now
    if not updated_at:
        updated_at = now

    # Priority (default to 2 if missing or invalid)
    priority = beads_data.get("priority", 2)
    try:
        priority = int(priority)
        if not 0 <= priority <= 4:
            warnings.append(f"Priority {priority} out of range, defaulting to 2")
            priority = 2
    except (ValueError, TypeError):
        warnings.append(f"Invalid priority '{priority}', defaulting to 2")
        priority = 2

    # Build notes from metadata
    notes = build_notes(
        beads_data.get("created_by"),
        beads_data.get("close_reason")
    )

    # Create task
    task = Task(
        id=task_id,
        title=title,
        description=beads_data.get("description", ""),
        status=status,
        priority=priority,
        type=task_type,
        assignee=beads_data.get("owner"),
        created_at=created_at,
        updated_at=updated_at,
        closed_at=closed_at,
        labels=[],
        dependencies=[],
        notes=notes,
    )

    return task, warnings


def import_from_beads(args) -> None:
    """Import tasks from beads JsonLines format.

    Args:
        args: Argument namespace with filepath, dry_run, and json attributes
    """
    config = Config.load()
    storage = Storage(config=config)

    # Validate input file
    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    # Load existing tasks to check for ID conflicts
    existing_tasks = storage.load_tasks()
    existing_ids = {task.id for task in existing_tasks}

    # Track statistics
    stats = {
        "total_lines": 0,
        "imported": 0,
        "skipped": 0,
        "errors": 0,
    }
    details = []

    # Print header (non-JSON mode)
    if not args.json:
        print(f"\nImporting from beads: {filepath}\n")

    # Process file line by line
    with open(filepath, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            stats["total_lines"] += 1

            try:
                # Parse JSON
                beads_data = json.loads(line)

                # Convert to Task
                task, warnings = convert_beads_task(beads_data)

                # Check for ID conflict
                if task.id in existing_ids:
                    stats["skipped"] += 1
                    msg = f"Skipped (ID already exists)"
                    details.append({
                        "id": task.id,
                        "status": "skipped",
                        "reason": "ID already exists"
                    })
                    if not args.json:
                        print(f"{colorize('⚠', YELLOW)} {colorize(task.id, YELLOW)}: {msg}")
                    continue

                # Save task (unless dry-run)
                if not args.dry_run:
                    storage.save_task(task)
                    existing_ids.add(task.id)

                stats["imported"] += 1

                # Build detail entry
                detail = {
                    "id": task.id,
                    "title": task.title,
                    "type": task.type,
                    "status": "imported"
                }
                if warnings:
                    detail["warnings"] = warnings
                details.append(detail)

                # Print progress (non-JSON mode)
                if not args.json:
                    icon = "✓" if not args.dry_run else "○"
                    color = GREEN if not args.dry_run else YELLOW
                    type_label = task.type.capitalize()

                    # Truncate title if too long
                    display_title = task.title
                    if len(display_title) > 60:
                        display_title = display_title[:57] + "..."

                    msg = f"{type_label}: {display_title}"
                    print(f"{colorize(icon, color)} {colorize(task.id, color)}: {msg}")

                    # Show warnings
                    for warning in warnings:
                        print(f"  {colorize('⚠', YELLOW)} {warning}")

            except json.JSONDecodeError as e:
                stats["errors"] += 1
                details.append({
                    "line": line_num,
                    "status": "error",
                    "error": f"Invalid JSON: {e}"
                })
                if not args.json:
                    print(f"{colorize('✗', RED)} Line {line_num}: Invalid JSON - {e}")

            except ValueError as e:
                stats["errors"] += 1
                details.append({
                    "line": line_num,
                    "status": "error",
                    "error": str(e)
                })
                if not args.json:
                    print(f"{colorize('✗', RED)} Line {line_num}: {e}")

            except Exception as e:
                stats["errors"] += 1
                details.append({
                    "line": line_num,
                    "status": "error",
                    "error": f"Unexpected error: {e}"
                })
                if not args.json:
                    print(f"{colorize('✗', RED)} Line {line_num}: Unexpected error - {e}")

    # Output results
    if args.json:
        output = {
            "source_file": str(filepath),
            "dry_run": args.dry_run,
            "stats": stats,
            "details": details
        }
        print_json(output)
    else:
        # Print summary
        print(f"\n{colorize('Summary:', GREEN if stats['errors'] == 0 else YELLOW)}")

        if args.dry_run:
            print(f"  {colorize('(Dry run - no changes made)', YELLOW)}")

        print(f"  Imported: {colorize(str(stats['imported']), GREEN)}")

        if stats["skipped"] > 0:
            print(f"  Skipped:  {colorize(str(stats['skipped']), YELLOW)}")

        if stats["errors"] > 0:
            print(f"  Errors:   {colorize(str(stats['errors']), RED)}")

        print()
