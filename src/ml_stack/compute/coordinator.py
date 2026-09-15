from __future__ import annotations
import json
from pathlib import Path
from .judge import ResultJudge
from .runner import ExperimentResult, LocalExperimentRunner

class ExperimentCoordinator:
    def __init__(self, root: str | Path): self.root = Path(root); self.out = self.root / ".ml-stack" / "experiments"; self.out.mkdir(parents=True, exist_ok=True)
    def run_bounded(self, data_path: str | Path, target: str, hypotheses: list[str], seed: int = 0) -> list[ExperimentResult]:
        if len(hypotheses) != 3: raise ValueError("exactly three one-main-variable hypotheses are required")
        runner = LocalExperimentRunner(); results = []
        for index, hypothesis in enumerate(hypotheses, 1):
            result = runner.run(data_path, target, f"exp-{index}", hypothesis, seed + index); runner.write(result, self.out / f"exp-{index}.json"); results.append(result)
        decision = ResultJudge().compare(results)
        (self.out / "decision.json").write_text(json.dumps({"accepted": decision.accepted, "reason": decision.reason, "selected": decision.selected.experiment_id if decision.selected else None}, indent=2) + "\n", encoding="utf-8")
        return results
