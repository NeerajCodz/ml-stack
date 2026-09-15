"""Environment and project configuration with secret-safe serialization."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None: return default
    return value.lower() in {"1", "true", "yes", "on"}

@dataclass(slots=True)
class Settings:
    root: Path = field(default_factory=Path.cwd)
    state_dir: Path | None = None
    host: str = "generic"
    database: Path | None = None
    allow_local_tools: bool = False
    offline: bool = False
    budget_usd: float | None = None
    log_level: str = "INFO"
    secret_refs: dict[str, str] = field(default_factory=dict)
    def __post_init__(self) -> None:
        self.root = Path(self.root).resolve(); self.state_dir = (self.state_dir or self.root / ".ml-stack").resolve(); self.database = (self.database or self.state_dir / "ledger.sqlite").resolve()
    @property
    def config_path(self) -> Path: return self.state_dir / "config.json"
    def safe_dict(self) -> dict[str, Any]: return {"root":str(self.root),"state_dir":str(self.state_dir),"host":self.host,"database":str(self.database),"allow_local_tools":self.allow_local_tools,"offline":self.offline,"budget_usd":self.budget_usd,"log_level":self.log_level,"secret_refs":sorted(self.secret_refs)}
    def ensure_state(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        for name in ("requirements", "research", "experiments", "runs", "versions", "cache", "locks", "events", "artifacts"): (self.state_dir / name).mkdir(exist_ok=True)
        for name in ("exp", "research", "bench", "notes"): (self.root / name).mkdir(exist_ok=True)
        if not self.config_path.exists(): self.config_path.write_text(json.dumps(self.safe_dict(), indent=2) + "\n", encoding="utf-8")

def load_settings(root: str | Path | None = None, environ: dict[str, str] | None = None) -> Settings:
    explicit = dict(os.environ if environ is None else environ)
    base = Path(root or explicit.get("ML_STACK_ROOT", Path.cwd())).resolve(); merged: dict[str, str] = {}
    dotenv = base / ".env"
    if dotenv.exists():
        for line in dotenv.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key.startswith("ML_STACK_"): merged[key] = value.strip().strip('"\'')
    merged.update(explicit)
    state = Path(merged["ML_STACK_STATE_DIR"]).resolve() if merged.get("ML_STACK_STATE_DIR") else base / ".ml-stack"
    return Settings(root=base, state_dir=state, host=merged.get("ML_STACK_HOST", "generic"), allow_local_tools=_bool(merged.get("ML_STACK_ALLOW_LOCAL_TOOLS")), offline=_bool(merged.get("ML_STACK_OFFLINE")), budget_usd=float(merged["ML_STACK_BUDGET_USD"]) if merged.get("ML_STACK_BUDGET_USD") else None, log_level=merged.get("ML_STACK_LOG_LEVEL", "INFO"), secret_refs={k:v for k,v in merged.items() if k.startswith("ML_STACK_SECRET_REF_")})
