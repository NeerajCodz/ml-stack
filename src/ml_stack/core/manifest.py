from __future__ import annotations
import hashlib
from pathlib import Path

def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()

def tree_hash(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)).replace("\\", "/"): file_hash(p) for p in sorted(root.rglob("*")) if p.is_file()}
