"""Task data model and validation."""

from dataclasses import dataclass, field, replace, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Task model with validation."""

    id: str
    title: str
    created_at: str
    updated_at: str
    description: str = ""
    type: str = "task"  # task, bug, feature, epic, chore
    status: str = "open"  # open, in_progress, to_review, closed
    priority: int = 2  # 0-4 (0=highest/critical, 2=medium, 4=backlog)
    assignee: Optional[str] = None
    labels: list[str] = field(default_factory=list)
    closed_at: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)  # task IDs this task depends on
    notes: str = ""

    @classmethod
    def create(cls, id: str, title: str, **kwargs) -> "Task":
        """Create a new task with timestamps."""
        now = datetime.utcnow().isoformat() + "Z"
        return cls(
            id=id,
            title=title,
            created_at=now,
            updated_at=now,
            **kwargs
        )

    def update_fields(self, **kwargs) -> "Task":
        """Update task fields and set updated_at timestamp."""
        now = datetime.utcnow().isoformat() + "Z"
        update_data = {**kwargs, "updated_at": now}

        # Handle status change to closed
        if kwargs.get("status") == "closed" and self.status != "closed":
            update_data["closed_at"] = now

        return replace(self, **update_data)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary."""
        return cls(**data)
