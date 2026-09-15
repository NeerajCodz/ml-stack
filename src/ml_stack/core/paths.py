from __future__ import annotations
from pathlib import Path

def within(root: str | Path, candidate: str | Path) -> Path:
    base = Path(root).resolve(); path = Path(candidate).resolve()
    if path != base and base not in path.parents: raise ValueError(f"path escapes project root: {candidate}")
    return path
