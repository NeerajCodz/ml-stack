"""Provider adapters with explicit configuration boundaries.

These adapters define the common provider surface without pretending a remote
service is available.  Network integrations can be layered on top without
moving scientific logic into provider code.
"""
from __future__ import annotations

from typing import Any

from ..schemas import JobSpec
from .base import JobStatus, Provider, ProviderUnavailableError



class UnconfiguredProvider(Provider):
    configured = False

    def __init__(self, *, endpoint: str | None = None, token: str | None = None, **config: Any):
        self.endpoint = endpoint
        # Keep only presence, never retain a secret in a status/error payload.
        self._has_token = bool(token)
        self.config = {key: value for key, value in config.items() if key not in {"token", "secret"}}
        self.configured = bool(endpoint or config.get("configured", False))

    def capabilities(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "configured": self.configured,
            "available": False,
            "cpu": None,
            "gpu": None,
            "free": None,
            "reason": "provider integration is not configured" if not self.configured else "remote adapter unavailable",
        }

    def _unavailable(self) -> None:
        raise ProviderUnavailableError(
            f"{self.name} is unavailable; configure its endpoint/credentials before submitting jobs"
        )

    def submit(self, spec: JobSpec) -> str:
        self._unavailable()
        raise AssertionError("unreachable")

    def status(self, job_id: str) -> JobStatus:
        return JobStatus(job_id, "ORPHANED", message="remote status unavailable")

    def logs(self, job_id: str) -> str:
        return ""

    def cancel(self, job_id: str) -> None:
        self._unavailable()

    def artifacts(self, job_id: str) -> list[str]:
        return []

    def cleanup(self, job_id: str) -> None:
        return None


class HFJobsProvider(UnconfiguredProvider):
    name = "hf_jobs"


class HFSpaceProvider(UnconfiguredProvider):
    name = "hf_space"


class KaggleProvider(UnconfiguredProvider):
    name = "kaggle"


class ModalProvider(UnconfiguredProvider):
    name = "modal"


class SSHProvider(UnconfiguredProvider):
    name = "ssh"


class SlurmProvider(UnconfiguredProvider):
    name = "slurm"


# Common spelling variants are harmless aliases, not separate provider names.
HfJobsProvider = HFJobsProvider
HfSpaceProvider = HFSpaceProvider
