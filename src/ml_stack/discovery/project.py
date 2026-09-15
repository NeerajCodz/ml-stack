from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

TEXT_EXTENSIONS = {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".csv", ".tsv"}

def discover_project(root: str | Path) -> dict[str, Any]:
    root = Path(root).resolve(); files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".ml-stack" in path.parts or ".git" in path.parts: continue
        stat = path.stat(); digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files.append({"path": str(path.relative_to(root)).replace("\\", "/"), "size": stat.st_size, "sha256": digest, "suffix": path.suffix.lower()})
    rules = [f["path"] for f in files if Path(f["path"]).name.lower() in {"readme.md", "license", "pyproject.toml", "requirements.txt", "spec.md"}]
    result = {"root": str(root), "files": files, "rules": rules, "task_class": _classify(files), "unknowns": []}
    (root / ".ml-stack" / "project-inventory.json").parent.mkdir(parents=True, exist_ok=True)
    (root / ".ml-stack" / "project-inventory.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result

def _classify(files: list[dict[str, Any]]) -> str:
    names = {Path(f["path"]).name.lower() for f in files}
    if any(n in names for n in {"train.py", "model.py", "dataset.py"}): return "supervised_ml"
    if any(f["suffix"] in {".csv", ".parquet", ".arrow"} for f in files): return "tabular_ml"
    return "unknown_ml_task"
