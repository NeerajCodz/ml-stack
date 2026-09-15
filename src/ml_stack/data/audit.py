from __future__ import annotations
import csv, json
from pathlib import Path
from typing import Any

def audit_file(path: str | Path, target: str | None = None) -> dict[str, Any]:
    path = Path(path); suffix = path.suffix.lower(); result: dict[str, Any] = {"path":str(path),"format":suffix.lstrip("."),"size":path.stat().st_size,"rows":None,"columns":[],"issues":[]}
    if suffix in {".csv", ".tsv"}:
        samples = []; count = 0; ids = set(); duplicate_ids = 0
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter="\t" if suffix == ".tsv" else ","); result["columns"] = reader.fieldnames or []
            for row in reader:
                count += 1
                if len(samples) < 100: samples.append(row)
                if row.get("id") is not None:
                    if row["id"] in ids: duplicate_ids += 1
                    ids.add(row["id"])
        result["rows"] = count; result["sample"] = samples
        if duplicate_ids: result["issues"].append({"type":"duplicate_ids","count":duplicate_ids})
    elif suffix in {".json", ".jsonl"}:
        if suffix == ".jsonl":
            samples = []; count = 0
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip(): count += 1; samples.append(json.loads(line)) if len(samples) < 100 else None
            rows = samples; result["rows"] = count
        else:
            loaded = json.loads(path.read_text(encoding="utf-8")); rows = loaded if isinstance(loaded, list) else [loaded]; result["rows"] = len(rows); rows = rows[:100]
        result["columns"] = sorted({k for row in rows if isinstance(row, dict) for k in row}); result["sample"] = rows[:5]
    elif suffix in {".parquet", ".arrow", ".npy", ".npz"}: result["inspection"] = "metadata-only; optional dependency required for schema values"
    if target and target not in result["columns"]: result["issues"].append({"type":"missing_target","target":target})
    if target and result.get("sample"):
        values = [r.get(target) for r in result["sample"] if isinstance(r, dict)]
        if len(set(map(str, values))) <= 1: result["issues"].append({"type":"constant_target","target":target})
    return result

def audit_path(path: str | Path, target: str | None = None) -> list[dict[str, Any]]:
    p = Path(path); return [audit_file(p, target)] if p.is_file() else [audit_file(x, target) for x in sorted(p.rglob("*")) if x.suffix.lower() in {".csv",".tsv",".json",".jsonl",".parquet",".arrow",".npy",".npz"}]
