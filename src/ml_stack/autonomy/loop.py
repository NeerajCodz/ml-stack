from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True, slots=True)
class StopPolicy:
    max_experiments: int = 3
    budget_usd: float | None = None
    target_reached: Callable[[dict], bool] | None = None

class AutonomousLoop:
    def __init__(self, policy: StopPolicy): self.policy = policy
    def run(self, execute: Callable[[int], dict]) -> list[dict]:
        results = []
        for index in range(self.policy.max_experiments):
            result = execute(index); results.append(result)
            if self.policy.target_reached and self.policy.target_reached(result): break
            if result.get("fatal_ambiguity") or result.get("user_stop"): break
        return results
