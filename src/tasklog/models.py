"""Task data model and validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Task(BaseModel):
    """Task model with validation."""

    id: str
    title: str
    description: str = ""
    type: str = "task"  # task, bug, feature, epic, chore
    status: str = "open"  # open, in_progress, to_review, closed
    priority: int = 2  # 0-4 (0=highest/critical, 2=medium, 4=backlog)
    assignee: Optional[str] = None
    labels: list[str] = Field(default_factory=list)
    created_at: str
    updated_at: str
    closed_at: Optional[str] = None
    dependencies: list[str] = Field(default_factory=list)  # task IDs this task depends on
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

        return self.model_copy(update=update_data)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary."""
        return cls(**data)
