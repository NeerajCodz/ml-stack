from __future__ import annotations
import os, subprocess, threading, uuid
from pathlib import Path
from ..schemas import JobSpec
from .base import JobStatus, Provider

class LocalProvider(Provider):
    name = "local"
    def __init__(self): self._jobs: dict[str, subprocess.Popen[str]] = {}; self._workspaces: dict[str, Path] = {}; self._lock = threading.Lock()
    def capabilities(self): return {"cpu": True, "gpu": False, "network": True, "free": True}
    def submit(self, spec: JobSpec) -> str:
        job_id = spec.job_id or f"local-{uuid.uuid4().hex[:12]}"; workspace = Path(spec.workspace).resolve(); workspace.mkdir(parents=True, exist_ok=True)
        stdout = (workspace / "stdout.log").open("w", encoding="utf-8"); stderr = (workspace / "stderr.log").open("w", encoding="utf-8")
        process = subprocess.Popen(spec.command, cwd=workspace, stdout=stdout, stderr=stderr, text=True, env={**os.environ, **spec.environment})
        with self._lock: self._jobs[job_id] = process; self._workspaces[job_id] = workspace
        return job_id
    def status(self, job_id):
        with self._lock: process = self._jobs.get(job_id)
        if process is None: return JobStatus(job_id, "UNKNOWN", message="job not found")
        code = process.poll(); return JobStatus(job_id, "RUNNING" if code is None else ("SUCCEEDED" if code == 0 else "FAILED"), code)
    def logs(self, job_id):
        workspace = self._workspaces.get(job_id); path = workspace / "stdout.log" if workspace else None
        return path.read_text(encoding="utf-8") if path and path.exists() else ""
    def cancel(self, job_id):
        with self._lock: process = self._jobs.get(job_id)
        if process and process.poll() is None: process.terminate()
    def artifacts(self, job_id):
        workspace = self._workspaces.get(job_id); return [str(path) for path in workspace.iterdir() if path.is_file() and path.name not in {"stdout.log","stderr.log"}] if workspace and workspace.exists() else []
