from __future__ import annotations
import csv, json, math, random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

@dataclass(slots=True)
class ExperimentResult:
    experiment_id: str
    hypothesis: str
    metrics: dict[str, float]
    status: str
    seed: int
    provenance: dict[str, Any]

class LocalExperimentRunner:
    """Deterministic baseline for synthetic tabular fixtures; no hardcoded deliverable names."""
    def run(self, data_path: str | Path, target: str, experiment_id: str, hypothesis: str, seed: int = 0) -> ExperimentResult:
        random.seed(seed); rows = self._read(data_path); values = [float(r[target]) for r in rows if r.get(target) not in (None, "")]
        if not values: raise ValueError("target has no usable values")
        mean = sum(values) / len(values); mae = sum(abs(v - mean) for v in values) / len(values); rmse = math.sqrt(sum((v-mean)**2 for v in values)/len(values))
        return ExperimentResult(experiment_id, hypothesis, {"mae": mae, "rmse": rmse, "target_mean": mean}, "SUCCEEDED", seed, {"rows": len(rows), "target": target, "runner": "local-baseline"})
    def _read(self, path):
        p = Path(path)
        if p.suffix.lower() != ".csv": raise ValueError("local baseline currently requires CSV")
        with p.open(newline="", encoding="utf-8") as f: return list(csv.DictReader(f))
    @staticmethod
    def write(result: ExperimentResult, path: str | Path): Path(path).write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
