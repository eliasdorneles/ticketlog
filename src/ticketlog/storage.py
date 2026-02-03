"""JSON Lines storage for tasks."""

import json
from pathlib import Path
from typing import Optional
from .models import Task


class Storage:
    """Manages task storage in JSON Lines format."""

    def __init__(self, filepath: str = "ticketlog.jl"):
        self.filepath = Path(filepath)
        self._next_id: Optional[int] = None

    def load_tasks(self) -> list[Task]:
        """Load tasks from JSON Lines file, keeping only the latest version of each task."""
        if not self.filepath.exists():
            return []

        tasks_by_id = {}
        max_id = 0

        with open(self.filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                data = json.loads(line)
                task = Task.from_dict(data)
                tasks_by_id[task.id] = task

                # Track max ID for next ID generation
                if task.id.startswith("tl-"):
                    try:
                        task_num = int(task.id.split("-")[1])
                        max_id = max(max_id, task_num)
                    except (IndexError, ValueError):
                        pass

        self._next_id = max_id + 1
        return list(tasks_by_id.values())

    def save_task(self, task: Task) -> None:
        """Append task to JSON Lines file."""
        with open(self.filepath, "a") as f:
            f.write(json.dumps(task.to_dict()) + "\n")

    def get_next_id(self) -> str:
        """Generate next task ID."""
        if self._next_id is None:
            # Load tasks to initialize next_id
            self.load_tasks()
            if self._next_id is None:
                self._next_id = 1

        task_id = f"tl-{self._next_id}"
        self._next_id += 1
        return task_id

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Find a task by ID."""
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        return self.load_tasks()
