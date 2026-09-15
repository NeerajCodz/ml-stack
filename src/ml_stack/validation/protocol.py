from __future__ import annotations
import hashlib, json
from dataclasses import asdict, dataclass
from pathlib import Path

class ValidationError(ValueError): pass
@dataclass(frozen=True, slots=True)
class ValidationLock:
    revision: int
    split: str
    folds: int
    seed: int
    metric: str
    threshold: float
    protocol: str
    digest: str = ""
    def seal(self) -> "ValidationLock":
        raw = asdict(self); raw["digest"] = ""
        return ValidationLock(**{**raw, "digest": hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()})
    def validate_metric(self, value: float) -> None:
        if self.metric in {"accuracy", "f1", "roc_auc"} and not 0 <= value <= 1: raise ValidationError(f"{self.metric} must be between 0 and 1")
        if self.metric in {"rmse", "mae", "loss"} and value < 0: raise ValidationError(f"{self.metric} cannot be negative")
    def write(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")
