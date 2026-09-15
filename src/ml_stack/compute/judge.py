from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .runner import ExperimentResult

@dataclass(frozen=True, slots=True)
class Decision:
    accepted: bool
    reason: str
    selected: ExperimentResult | None = None

class ResultJudge:
    def __init__(self, metric: str = "mae", threshold: float | None = None): self.metric, self.threshold = metric, threshold
    def compare(self, results: Iterable[ExperimentResult]) -> Decision:
        candidates = [r for r in results if r.status == "SUCCEEDED" and self.metric in r.metrics]
        if not candidates: return Decision(False, "no compatible successful results")
        selected = min(candidates, key=lambda r: r.metrics[self.metric])
        if self.threshold is not None and selected.metrics[self.metric] > self.threshold: return Decision(False, f"best {self.metric} exceeds threshold", selected)
        if len({r.provenance.get("target") for r in candidates}) != 1: return Decision(False, "results use incompatible targets")
        return Decision(True, "best compatible result passed gates", selected)
