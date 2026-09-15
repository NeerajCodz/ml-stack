from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

class LifecycleState(StrEnum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    ORPHANED = "ORPHANED"
    DONE = "DONE"

class OperationKind(StrEnum):
    USER_INPUT = "USER_INPUT"
    APPROVAL = "APPROVAL"
    UNDO = "UNDO"
    COMPACT = "COMPACT"
    NEW = "NEW"
    RESUME = "RESUME"
    SHUTDOWN = "SHUTDOWN"

@dataclass(slots=True)
class Operation:
    kind: OperationKind
    payload: dict[str, Any]
    operation_id: str = ""
