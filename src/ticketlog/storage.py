"""JSON Lines storage for tasks."""

import json
import random
import string
import sys
from pathlib import Path
from typing import Optional
from .models import Task
from .config import Config
from .utils import colorize, YELLOW


class Storage:
    """Manages task storage in JSON Lines format."""

    def __init__(self, filepath: str = "ticketlog.jsonl", config: Optional[Config] = None):
        self.filepath = Path(filepath)
        self.config = config or Config()
        self._total_lines = 0
        self._unique_count = 0
        self._dead_history_warned = False

    def load_tasks(self) -> list[Task]:
        """Load tasks from JSON Lines file, keeping only the latest version of each task."""
        if not self.filepath.exists():
            self._total_lines = 0
            self._unique_count = 0
            return []

        tasks_by_id = {}
        total_lines = 0

        with open(self.filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                total_lines += 1
                data = json.loads(line)
                task = Task.from_dict(data)
                tasks_by_id[task.id] = task

        self._total_lines = total_lines
        self._unique_count = len(tasks_by_id)

        return list(tasks_by_id.values())

    @property
    def dead_history_ratio(self) -> float:
        """Ratio of dead (duplicate) lines to total lines."""
        if self._total_lines == 0:
            return 0.0
        return (self._total_lines - self._unique_count) / self._total_lines

    def check_dead_history(self) -> None:
        """Print a warning to stderr if dead history exceeds the configured threshold."""
        if self._dead_history_warned:
            return
        ratio = self.dead_history_ratio
        if ratio > self.config.dead_history_threshold:
            self._dead_history_warned = True
            pct = ratio * 100
            threshold_pct = self.config.dead_history_threshold * 100
            msg = (
                f"\u26a0 {pct:.1f}% of the log is dead history "
                f"(threshold: {threshold_pct:.0f}%). "
                f"Run 'tl clean' to compact."
            )
            print(colorize(msg, YELLOW), file=sys.stderr)

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
