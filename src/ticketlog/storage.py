"""JSON Lines storage for tasks."""

import json
import random
import string
from pathlib import Path
from typing import Optional
from .models import Task
from .config import Config


class Storage:
    """Manages task storage in JSON Lines format."""

    def __init__(self, filepath: str = "ticketlog.jsonl", config: Optional[Config] = None):
        self.filepath = Path(filepath)
        self.config = config or Config()

    def load_tasks(self) -> list[Task]:
        """Load tasks from JSON Lines file, keeping only the latest version of each task."""
        if not self.filepath.exists():
            return []

        tasks_by_id = {}

        with open(self.filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                data = json.loads(line)
                task = Task.from_dict(data)
                tasks_by_id[task.id] = task

        return list(tasks_by_id.values())

    def save_task(self, task: Task) -> None:
        """Append task to JSON Lines file."""
        with open(self.filepath, "a") as f:
            f.write(json.dumps(task.to_dict()) + "\n")

    def _generate_random_id(self, existing_ids: set[str]) -> str:
        """Generate random 3-letter alphanumeric ID.

        Args:
            existing_ids: Set of existing task IDs to avoid collisions

        Returns:
            New unique task ID

        Raises:
            ValueError: If unable to generate unique ID after 10 attempts
        """
        chars = string.ascii_lowercase + string.digits

        for _ in range(10):
            suffix = "".join(random.choices(chars, k=3))
            task_id = f"{self.config.prefix}-{suffix}"
            if task_id not in existing_ids:
                return task_id

        raise ValueError(
            f"Failed to generate unique ID with prefix '{self.config.prefix}' after 10 attempts"
        )

    def get_next_id(self) -> str:
        """Generate next task ID using random 3-letter suffix.

        Returns:
            New unique task ID
        """
        tasks = self.load_tasks()
        existing_ids = {task.id for task in tasks}
        return self._generate_random_id(existing_ids)

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
