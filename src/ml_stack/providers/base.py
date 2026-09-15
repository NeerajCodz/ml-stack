from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from ..schemas import JobSpec

class ProviderError(RuntimeError):
    """Base error for provider boundary failures."""


class ProviderUnavailableError(ProviderError):
    """Raised when a provider is not configured or reachable."""

@dataclass(slots=True)
class JobStatus:
    job_id: str
    state: str
    exit_code: int | None = None
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

class Provider(ABC):
    name: str
    @abstractmethod
    def capabilities(self) -> dict[str, Any]: ...
    @abstractmethod
    def submit(self, spec: JobSpec) -> str: ...
    @abstractmethod
    def status(self, job_id: str) -> JobStatus: ...
    @abstractmethod
    def logs(self, job_id: str) -> str: ...
    @abstractmethod
    def cancel(self, job_id: str) -> None: ...
    @abstractmethod
    def artifacts(self, job_id: str) -> list[str]: ...
    def cleanup(self, job_id: str) -> None: pass
