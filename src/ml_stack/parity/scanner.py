from __future__ import annotations
import json
from pathlib import Path

class ParityScanner:
    def __init__(self, root: str | Path): self.root = Path(root)
    def scan(self) -> dict:
        functional = [str(path.relative_to(self.root)).replace("\\", "/") for path in self.root.joinpath("src/ml_stack").rglob("*.py") if path.name != "__init__.py"]
        manifest_path = self.root / "parity-manifest.json"
        expected = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
        if not any(expected.get(k) for k in ("implemented", "host_provided", "presentation_only", "unavailable")):
            expected = {"implemented": functional, "host_provided": [], "presentation_only": [], "unavailable": []}
        classified = set().union(*(set(expected.get(k, [])) for k in ("implemented", "host_provided", "presentation_only", "unavailable")))
        additions = sorted(set(functional) - classified)
        return {"functional_files": sorted(functional), "unclassified": additions, "ok": not additions}
