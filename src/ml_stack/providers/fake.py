"""Deterministic provider used for contract checks and offline operation."""
from __future__ import annotations

from dataclasses import replace
from threading import RLock
from typing import Iterable

from ..schemas import JobSpec
from .base import JobStatus, Provider


class FakeProvider(Provider):
    """In-memory provider with explicit state transitions and no execution.

    It is intentionally not a scientific runner.  Callers may complete or
    fail a submitted job to exercise supervisor/reconciliation behavior.
    """

    name = "fake"

    def __init__(self, *, capabilities: dict[str, object] | None = None):
        self._jobs: dict[str, tuple[JobSpec, JobStatus]] = {}
        self._artifacts: dict[str, list[str]] = {}
        self._lock = RLock()
        self._capabilities = {
            "configured": True,
            "available": True,
            "cpu": True,
            "gpu": None,
            "free": None,
        }
        if capabilities:
            self._capabilities.update(capabilities)

    def capabilities(self) -> dict[str, object]:
        return dict(self._capabilities)

    def submit(self, spec: JobSpec) -> str:
        with self._lock:
            job_id = spec.job_id or f"fake-{len(self._jobs) + 1}"
            if job_id in self._jobs:
                raise ValueError(f"job already exists: {job_id}")
            self._jobs[job_id] = (replace(spec, job_id=job_id), JobStatus(job_id, "QUEUED"))
            self._artifacts[job_id] = []
            return job_id

    def status(self, job_id: str) -> JobStatus:
        with self._lock:
            item = self._jobs.get(job_id)
            if item is None:
                return JobStatus(job_id, "UNKNOWN", message="job not found")
            return item[1]

    def logs(self, job_id: str) -> str:
        return "" if job_id not in self._jobs else "fake provider does not execute commands\n"

    def cancel(self, job_id: str) -> None:
        with self._lock:
            if job_id not in self._jobs:
                return
            spec, status = self._jobs[job_id]
            if status.state not in {"SUCCEEDED", "FAILED", "CANCELED", "DONE"}:
                self._jobs[job_id] = (spec, replace(status, state="CANCELED"))

    def artifacts(self, job_id: str) -> list[str]:
        with self._lock:
            return list(self._artifacts.get(job_id, []))

    def set_status(self, job_id: str, state: str, *, exit_code: int | None = None, message: str = "") -> None:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(job_id)
            spec, _ = self._jobs[job_id]
            self._jobs[job_id] = (spec, JobStatus(job_id, state, exit_code, message))

    def complete(self, job_id: str, *, artifacts: Iterable[str] = ()) -> None:
        with self._lock:
            self.set_status(job_id, "SUCCEEDED", exit_code=0)
            self._artifacts[job_id] = list(artifacts)

    def fail(self, job_id: str, message: str = "") -> None:
        self.set_status(job_id, "FAILED", exit_code=1, message=message)
