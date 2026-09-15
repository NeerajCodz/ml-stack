from __future__ import annotations
import csv, json
from pathlib import Path

def audit_deliverable(path: str | Path, required_columns: list[str] | None = None, max_rows: int | None = None) -> dict:
    path = Path(path); required_columns = required_columns or []
    result = {"path": str(path), "valid": True, "issues": [], "rows": 0, "columns": []}
    if not path.exists(): result["valid"] = False; result["issues"].append("missing file"); return result
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f); result["columns"] = reader.fieldnames or []
            if any(c not in result["columns"] for c in required_columns): result["valid"] = False; result["issues"].append("missing required columns")
            for row in reader:
                result["rows"] += 1
                if max_rows is not None and result["rows"] > max_rows: result["valid"] = False; result["issues"].append("row limit exceeded"); break
    elif path.suffix.lower() == ".json":
        try: value = json.loads(path.read_text(encoding="utf-8")); result["rows"] = len(value) if isinstance(value, list) else 1
        except json.JSONDecodeError: result["valid"] = False; result["issues"].append("invalid JSON")
    else: result["valid"] = False; result["issues"].append("unsupported deliverable format")
    if result["rows"] == 0: result["valid"] = False; result["issues"].append("empty deliverable")
    return result
