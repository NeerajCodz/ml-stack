"""Content-addressed artifact manifests.

The manifest is deliberately independent of wall-clock time: file hashes and the
manifest digest are reproducible for the same tree.  Timestamps, when included
in the JSON representation, are metadata only and never affect the digest.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = "1.0"


def hash_file(path: str | Path) -> str:
    """Return the SHA-256 digest of *path* without loading it into memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# The name used by ``core.manifest`` is kept as a convenient public alias.
file_hash = hash_file


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    path: str
    sha256: str
    size: int

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "sha256": self.sha256, "size": self.size}


@dataclass(frozen=True, slots=True)
class ArtifactManifest:
    """An immutable description of files produced by a job.

    ``root`` is informational and is intentionally excluded from ``digest`` so
    copying a result tree does not change its identity.
    """

    root: str
    files: tuple[ArtifactRecord, ...]
    schema_version: str = SCHEMA_VERSION
    created_at: str | None = None

    def canonical(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "files": [record.to_dict() for record in self.files],
        }

    def digest(self) -> str:
        encoded = json.dumps(self.canonical(), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    @property
    def manifest_hash(self) -> str:
        return self.digest()

    def to_dict(self) -> dict[str, object]:
        return {
            **self.canonical(),
            "root": self.root,
            "created_at": self.created_at,
            "digest": self.digest(),
        }


def _relative_files(root: Path, exclude: set[str]) -> Iterable[tuple[str, Path]]:
    root = root.resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in exclude:
            continue
        # A regular file cannot normally escape root, but this check prevents
        # surprising manifests if a platform reports unusual path semantics.
        if not path.resolve().is_relative_to(root):
            continue
        yield relative, path


def build_manifest(root: str | Path, *, exclude: Iterable[str] = ()) -> ArtifactManifest:
    """Hash all regular files below *root* in deterministic path order."""
    base = Path(root)
    if not base.is_dir():
        raise NotADirectoryError(base)
    excluded = {Path(item).as_posix() for item in exclude}
    records = tuple(
        ArtifactRecord(relative, hash_file(path), path.stat().st_size)
        for relative, path in _relative_files(base, excluded)
    )
    return ArtifactManifest(
        root=str(base),
        files=records,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def write_manifest(
    root: str | Path,
    destination: str | Path | None = None,
    *,
    exclude: Iterable[str] = (),
) -> ArtifactManifest:
    """Write a JSON manifest atomically and return the in-memory manifest."""
    base = Path(root)
    target = Path(destination) if destination is not None else base / "manifest.json"
    try:
        relative_target = target.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        relative_target = ""
    excluded = set(exclude)
    if relative_target:
        excluded.add(relative_target)
    manifest = build_manifest(base, exclude=excluded)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(manifest.to_dict(), stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, target)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    return manifest


def verify_manifest(manifest: ArtifactManifest | str | Path, root: str | Path | None = None) -> bool:
    """Verify every recorded file and reject missing or extra files."""
    manifest_path: Path | None = None
    if isinstance(manifest, ArtifactManifest):
        expected = manifest
    else:
        manifest_path = Path(manifest)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = ArtifactManifest(
            root=str(payload.get("root", manifest_path.parent)),
            files=tuple(ArtifactRecord(**item) for item in payload.get("files", [])),
            schema_version=str(payload.get("schema_version", SCHEMA_VERSION)),
            created_at=payload.get("created_at"),
        )
    base = Path(root) if root is not None else Path(expected.root)
    if not base.is_dir():
        return False
    exclude: set[str] = set()
    if manifest_path is not None:
        try:
            exclude.add(manifest_path.resolve().relative_to(base.resolve()).as_posix())
        except ValueError:
            pass
    actual = build_manifest(base, exclude=exclude)
    return actual.files == expected.files


# Descriptive aliases used by provider and compute callers.
create_manifest = build_manifest
capture_artifacts = build_manifest
