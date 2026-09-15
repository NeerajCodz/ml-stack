"""Small immutable content-addressed artifact store."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from .manifest import hash_file


class ArtifactStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _destination(self, digest: str) -> Path:
        return self.root / digest[:2] / digest

    def put(self, source: str | Path) -> str:
        source_path = Path(source)
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        digest = hash_file(source_path)
        destination = self._destination(digest)
        if destination.exists():
            if hash_file(destination) != digest:
                raise IOError(f"artifact digest collision: {digest}")
            return digest
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=f".{digest}.", dir=destination.parent)
        os.close(fd)
        try:
            shutil.copyfile(source_path, temporary)
            os.replace(temporary, destination)
        except BaseException:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise
        return digest

    def get(self, digest: str) -> Path:
        destination = self._destination(digest)
        if not destination.is_file() or hash_file(destination) != digest:
            raise FileNotFoundError(digest)
        return destination

    def contains(self, digest: str) -> bool:
        try:
            self.get(digest)
        except FileNotFoundError:
            return False
        return True
