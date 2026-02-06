"""Clean command implementation."""

import json
import os
import tempfile

from ..storage import Storage
from ..config import Config
from ..utils import colorize, print_json, GREEN, YELLOW


def clean_log(args) -> None:
    """Deduplicate the log file by keeping only the latest version of each task."""
    config = Config.load()
    storage = Storage(config=config)

    # Load all tasks (already deduplicates in memory)
    tasks = storage.load_tasks()

    if not tasks:
        if args.json:
            print_json({"message": "No tasks to clean"})
        else:
            print(colorize("No tasks to clean", YELLOW))
        return

    # Count original lines in file
    with open(storage.filepath, "r") as f:
        original_lines = sum(1 for line in f if line.strip())

    new_lines = len(tasks)
    removed_lines = original_lines - new_lines

    # Check if already clean
    if removed_lines == 0:
        if args.json:
            print_json({
                "message": "Log already clean",
                "lines": original_lines,
                "removed_lines": 0
            })
        else:
            print(colorize(f"Log already clean: {original_lines} lines (no duplicates)", GREEN))
        return

    # Write deduplicated tasks to temp file atomically
    temp_fd, temp_path = tempfile.mkstemp(
        dir=storage.filepath.parent,
        prefix=".ticketlog_tmp_",
        suffix=".jl"
    )

    try:
        # Write all tasks sorted by ID
        with os.fdopen(temp_fd, 'w') as f:
            for task in sorted(tasks, key=lambda t: t.id):
                f.write(json.dumps(task.to_dict()) + "\n")
            f.flush()
            os.fsync(f.fileno())

        # Atomically replace original file
        os.replace(temp_path, storage.filepath)

        # Output results
        if args.json:
            print_json({
                "original_lines": original_lines,
                "new_lines": new_lines,
                "removed_lines": removed_lines
            })
        else:
            print(colorize(f"Cleaned log: {original_lines} lines → {new_lines} lines (removed {removed_lines} duplicates)", GREEN))
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
