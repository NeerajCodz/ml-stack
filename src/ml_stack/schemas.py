"""Versioned public JSON contracts used by all transports."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar

SCHEMA_VERSION = "1.0"

@dataclass(slots=True)
class Requirement:
    text: str
    source: str = "user"
    confidence: float = 1.0
    claim_class: str = "requirement"
    locked: bool = False
    requirement_id: str = ""

@dataclass(slots=True)
class RequirementsLock:
    revision: int
    requirements: list[Requirement]
    digest: str
    schema_version: ClassVar[str] = SCHEMA_VERSION

@dataclass(slots=True)
class JobSpec:
    job_id: str
    provider: str
    command: list[str]
    workspace: str
    resources: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)
    seed: int | None = None

@dataclass(slots=True)
class RunRecord:
    run_id: str
    state: str
    job_id: str
    hypothesis_id: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)

@dataclass(slots=True)
class Event:
    event_id: int
    event_type: str
    payload: dict[str, Any]
    created_at: str
    run_id: str | None = None

@dataclass(slots=True)
class Manifest:
    version: str
    requirements_digest: str
    files: dict[str, str]
    created_at: str
    immutable: bool = True


def to_json(value: Any) -> dict[str, Any]:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    raise TypeError(f"unsupported schema object: {type(value)!r}")
