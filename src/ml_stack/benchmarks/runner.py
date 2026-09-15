from __future__ import annotations
import json, time
from pathlib import Path

def benchmark(name, fn, repeats: int = 1, output: str | Path | None = None):
    if repeats < 1: raise ValueError("repeats must be positive")
    durations = []; values = []
    for _ in range(repeats):
        started = time.perf_counter(); values.append(fn()); durations.append(time.perf_counter() - started)
    result = {"name": name, "repeats": repeats, "seconds": {"min": min(durations), "mean": sum(durations)/len(durations), "max": max(durations)}, "values": values}
    if output: Path(output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
