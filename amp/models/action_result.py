"""ActionResult model for action execution results."""

from dataclasses import dataclass, field
from typing import Optional, Any, Dict, List
from datetime import datetime
from enum import Enum


class ActionStatus(Enum):
    """Status of an action execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    PENDING = "pending"
    CANCELLED = "cancelled"


@dataclass
class ActionResult:
    """Result of executing an action."""

    status: ActionStatus = ActionStatus.SUCCESS
    message: str = ""

    data: Optional[Any] = None
    items: List[Any] = field(default_factory=list)
    total_items: int = 0

    error_code: Optional[str] = None
    error_details: Optional[str] = None

    execution_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    action_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    follow_up_actions: List[str] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.status == ActionStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        return self.status == ActionStatus.FAILURE

    @property
    def has_data(self) -> bool:
        return self.data is not None or len(self.items) > 0

    @classmethod
    def success(cls, message: str, data: Any = None, **kwargs) -> "ActionResult":
        return cls(status=ActionStatus.SUCCESS, message=message, data=data, **kwargs)

    @classmethod
    def failure(cls, message: str, error_code: str = None, error_details: str = None, **kwargs) -> "ActionResult":
        return cls(status=ActionStatus.FAILURE, message=message, error_code=error_code, error_details=error_details, **kwargs)

    @classmethod
    def partial(cls, message: str, data: Any = None, **kwargs) -> "ActionResult":
        return cls(status=ActionStatus.PARTIAL, message=message, data=data, **kwargs)

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "message": self.message,
            "data": str(self.data) if self.data else None,
            "items_count": len(self.items),
            "total_items": self.total_items,
            "error_code": self.error_code,
            "error_details": self.error_details,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "action_type": self.action_type,
            "parameters": self.parameters,
        }

    def to_llm_response(self) -> str:
        if self.is_success:
            response = self.message
            if self.items:
                response += "\n" + "\n".join(f"  - {item}" for item in self.items[:10])
                if len(self.items) > 10:
                    response += f"\n  ... and {len(self.items) - 10} more"
            return response
        else:
            return f"Error: {self.message}" + (f" ({self.error_details})" if self.error_details else "")

    def __str__(self) -> str:
        return f"[{self.status.value.upper()}] {self.message}"

    def __repr__(self) -> str:
        return f"ActionResult(status={self.status.value}, message='{self.message[:50]}...')"
