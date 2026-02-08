"""Task model for tracking AI agent tasks."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents an AI agent task."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING

    # Task details
    action_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Planning
    subtasks: List["Task"] = field(default_factory=list)
    parent_task_id: Optional[str] = None

    # Execution
    result: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Context
    user_input: str = ""
    llm_response: str = ""

    @property
    def is_complete(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)

    @property
    def duration_ms(self) -> Optional[int]:
        """Get task duration in milliseconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() * 1000)
        return None

    @property
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.attempts < self.max_attempts and self.status == TaskStatus.FAILED

    def start(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
        self.attempts += 1

    def complete(self, result: str) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result

    def fail(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error

    def cancel(self) -> None:
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()

    def add_subtask(self, subtask: "Task") -> None:
        """Add a subtask."""
        subtask.parent_task_id = self.id
        self.subtasks.append(subtask)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage/logging."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "action_type": self.action_type,
            "parameters": self.parameters,
            "result": self.result,
            "error": self.error,
            "attempts": self.attempts,
            "user_input": self.user_input,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
        }

    def __str__(self) -> str:
        return f"Task({self.id}: {self.description} [{self.status.value}])"

    def __repr__(self) -> str:
        return f"Task(id='{self.id}', action='{self.action_type}', status={self.status.value})"
