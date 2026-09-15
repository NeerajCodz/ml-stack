from __future__ import annotations
import json, shutil
from pathlib import Path
from ..core.manifest import tree_hash

class VersionManager:
    def __init__(self, root: str | Path): self.root = Path(root) / ".ml-stack" / "versions"; self.root.mkdir(parents=True, exist_ok=True)
    def next_version(self) -> str:
        values = [int(p.name[1:]) for p in self.root.glob("v*") if p.name[1:].isdigit()]; return f"v{max(values, default=0)+1}"
    def promote(self, source: str | Path, requirements_digest: str, output_name: str | None = None) -> Path:
        version = output_name or self.next_version(); destination = self.root / version
        if destination.exists(): raise FileExistsError(f"promoted version is immutable: {destination}")
        source = Path(source); shutil.copytree(source, destination)
        manifest = {"version": version, "requirements_digest": requirements_digest, "files": tree_hash(destination), "immutable": True}
        (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return destination
    def verify(self, version: str) -> bool:
        path = self.root / version; manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8")); current = tree_hash(path); current.pop("manifest.json", None); return all(current.get(k) == v for k, v in manifest["files"].items())
