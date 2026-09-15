"""Provider-neutral job lifecycle supervision.

The supervisor owns normalized lifecycle transitions and persistence while
providers only transport/execute a shared ``JobSpec``.  SQLite records are
metadata and state; provider output is never treated as a source of truth for
scientific results.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from ..core.ledger import Ledger
from ..core.redaction import redact
from ..schemas import JobSpec
from ..providers.base import JobStatus, Provider


_KNOWN_STATES = {"CREATED", "QUEUED", "RUNNING", "PAUSED", "SUCCEEDED", "FAILED", "CANCELED", "ORPHANED", "DONE"}
_STATE_ALIASES = {
    "PENDING": "QUEUED",
    "SUBMITTED": "QUEUED",
    "STARTED": "RUNNING",
    "COMPLETED": "SUCCEEDED",
    "SUCCESS": "SUCCEEDED",
    "CANCELLED": "CANCELED",
    "ERROR": "FAILED",
}


@dataclass(frozen=True, slots=True)
class JobRecord:
    job_id: str
    provider: str
    state: str
    submitted: bool = True
    message: str = ""
    exit_code: int | None = None


class JobSupervisor:
    def __init__(
        self,
        providers: Mapping[str, Provider] | Iterable[Provider] | Provider,
        ledger: Ledger | None = None,
    ):
        if isinstance(providers, Provider):
            providers = [providers]
        if isinstance(providers, Mapping):
            self.providers = dict(providers)
        else:
            self.providers = {provider.name: provider for provider in providers}
        self.ledger = ledger
        self._jobs: dict[str, str] = {}

    def provider(self, name: str) -> Provider:
        try:
            return self.providers[name]
        except KeyError as exc:
            raise ValueError(f"unknown provider: {name}") from exc

    @staticmethod
    def _safe_spec(spec: JobSpec) -> dict[str, Any]:
        payload = asdict(spec)
        # Do not persist environment values; they may carry credentials even
        # when a caller did not use a secret-looking variable name.
        payload["environment"] = {"keys": sorted(spec.environment)}
        return redact(payload)

    def _record(self, job_id: str, provider: str, status: JobStatus, *, spec: JobSpec | None = None) -> None:
        payload: dict[str, Any] = {
            "job_id": job_id,
            "provider": provider,
            "state": status.state,
            "exit_code": status.exit_code,
            "message": status.message,
            "metadata": redact(status.metadata),
        }
        if spec is not None:
            payload["spec"] = self._safe_spec(spec)
        if self.ledger is not None:
            self.ledger.put("jobs", job_id, payload)
            self.ledger.append("JOB_STATUS", payload, run_id=job_id)

    def submit(self, spec: JobSpec) -> str:
        provider = self.provider(spec.provider)
        job_id = provider.submit(spec)
        if not job_id:
            raise RuntimeError("provider returned an empty job id")
        self._jobs[job_id] = spec.provider
        status = JobStatus(job_id, "QUEUED", message="submitted")
        self._record(job_id, spec.provider, status, spec=spec)
        return job_id

    def _normalize(self, status: JobStatus) -> JobStatus:
        state = str(status.state).upper()
        state = _STATE_ALIASES.get(state, state)
        if state not in _KNOWN_STATES:
            return JobStatus(
                status.job_id,
                "ORPHANED",
                status.exit_code,
                status.message or f"unrecognized remote state: {status.state}",
                {**status.metadata, "remote_state": status.state},
            )
        return JobStatus(status.job_id, state, status.exit_code, status.message, status.metadata)

    def status(self, job_id: str) -> JobStatus:
        provider_name = self._jobs.get(job_id)
        if provider_name is None and self.ledger is not None:
            record = self.ledger.get("jobs", job_id)
            provider_name = str(record["payload"]["provider"]) if record else None
        if provider_name is None:
            return JobStatus(job_id, "ORPHANED", message="job is not known to the supervisor")
        provider = self.provider(provider_name)
        try:
            status = self._normalize(provider.status(job_id))
        except Exception as exc:
            status = JobStatus(job_id, "ORPHANED", message=f"status reconciliation failed: {type(exc).__name__}")
        self._record(job_id, provider_name, status)
        return status

    def reconcile(self, job_id: str) -> JobStatus:
        return self.status(job_id)

    def cancel(self, job_id: str) -> JobStatus:
        provider_name = self._jobs.get(job_id)
        if provider_name is None:
            record = self.ledger.get("jobs", job_id) if self.ledger is not None else None
            provider_name = str(record["payload"]["provider"]) if record else None
        if provider_name is None:
            return JobStatus(job_id, "ORPHANED", message="job is not known to the supervisor")
        provider = self.provider(provider_name)
        try:
            provider.cancel(job_id)
        except Exception as exc:
            status = JobStatus(job_id, "ORPHANED", message=f"cancel failed: {type(exc).__name__}")
        else:
            status = self._normalize(provider.status(job_id))
            if status.state in {"QUEUED", "RUNNING", "PAUSED"}:
                status = JobStatus(job_id, "CANCELED", message="cancellation requested")
        self._record(job_id, provider_name, status)
        return status

    def logs(self, job_id: str) -> str:
        provider_name = self._jobs.get(job_id)
        if provider_name is None:
            raise KeyError(job_id)
        return self.provider(provider_name).logs(job_id)

    def artifacts(self, job_id: str) -> list[str]:
        provider_name = self._jobs.get(job_id)
        if provider_name is None:
            raise KeyError(job_id)
        return list(self.provider(provider_name).artifacts(job_id))

    def cleanup(self, job_id: str) -> None:
        provider_name = self._jobs.get(job_id)
        if provider_name is None:
            return
        self.provider(provider_name).cleanup(job_id)


Supervisor = JobSupervisor
ComputeSupervisor = JobSupervisor
