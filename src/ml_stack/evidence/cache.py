"""Durable, offline-capable content-addressed evidence cache."""
from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable, Mapping

from .models import EvidenceRecord


class OfflineCacheMiss(LookupError):
    """Raised when an offline lookup has no cached representation."""


def _digest(value: bytes | str) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


class EvidenceCache:
    """Store evidence records and source bodies beneath a cache directory.

    Record identity excludes retrieval time and confidence, so repeated fetches
    reuse one immutable object. If a core ``Ledger`` is supplied, SQLite is the
    authoritative metadata source and JSON files are only materializations.
    """

    def __init__(self, root: str | Path, ledger: Any | None = None):
        self.root = Path(root)
        self.records_dir = self.root / "records"
        self.content_dir = self.root / "content"
        self.records_dir.mkdir(parents=True, exist_ok=True)
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.ledger = ledger

    @staticmethod
    def key(record: EvidenceRecord) -> str:
        return record.key

    def _record_path(self, key: str) -> Path:
        if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
            raise ValueError("invalid evidence cache key")
        return self.records_dir / f"{key}.json"

    @staticmethod
    def _atomic_write(destination: Path, value: str | bytes) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
        try:
            if isinstance(value, bytes):
                with os.fdopen(fd, "wb") as stream:
                    stream.write(value)
                    stream.flush()
                    os.fsync(stream.fileno())
            else:
                with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                    stream.write(value)
                    stream.flush()
                    os.fsync(stream.fileno())
            os.replace(temporary, destination)
        except BaseException:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise

    def put(self, record: EvidenceRecord, content: str | bytes | None = None) -> EvidenceRecord:
        """Persist a record and optional complete source body without overwriting it."""
        if content is not None and not record.content_hash:
            record = replace(record, content_hash=_digest(content))
        stored = record.with_record_id()
        destination = self._record_path(stored.key)
        existing = self.get(stored.key)
        if existing is not None:
            stored = existing
        else:
            if self.ledger is not None:
                self.ledger.put("evidence", stored.key, stored.as_dict())
            self._atomic_write(destination, json.dumps(stored.as_dict(), ensure_ascii=False, sort_keys=True, indent=2) + "\n")
        if content is not None:
            raw = content.encode("utf-8") if isinstance(content, str) else bytes(content)
            if stored.content_hash and _digest(raw) != stored.content_hash:
                raise ValueError("content does not match record content_hash")
            body_path = self.content_dir / stored.content_hash
            if not body_path.exists():
                self._atomic_write(body_path, raw)
        return stored

    cache = put

    def get(self, key: str) -> EvidenceRecord | None:
        """Return a record by key, repairing the file materialization if needed."""
        path = self._record_path(key)
        if self.ledger is not None:
            payload = self.ledger.get("evidence", key)
            if payload:
                record = EvidenceRecord.from_dict(payload["payload"])
                if record.key != key:
                    raise ValueError("ledger evidence key does not match record")
                encoded = json.dumps(record.as_dict(), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
                if not path.exists() or path.read_text(encoding="utf-8") != encoded:
                    self._atomic_write(path, encoded)
                return record
        if path.exists():
            return EvidenceRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
        return None

    retrieve = get

    def body(self, record_or_key: EvidenceRecord | str) -> bytes | None:
        key = record_or_key.key if isinstance(record_or_key, EvidenceRecord) else record_or_key
        record = self.get(key)
        if record is None or not record.content_hash:
            return None
        path = self.content_dir / record.content_hash
        if not path.exists():
            return None
        raw = path.read_bytes()
        if _digest(raw) != record.content_hash:
            raise ValueError("cached source body failed integrity check")
        return raw

    get_body = body

    def find(self, source_url: str, *, excerpt_hash: str | None = None, claim_class: str | None = None) -> list[EvidenceRecord]:
        """Find records deterministically, sorted by content-addressed key."""
        found: list[EvidenceRecord] = []
        for path in sorted(self.records_dir.glob("*.json"), key=lambda p: p.name):
            try:
                record = EvidenceRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if record.source_url != source_url:
                continue
            if excerpt_hash is not None and record.excerpt_hash != excerpt_hash:
                continue
            if claim_class is not None and record.claim_class != claim_class:
                continue
            found.append(record)
        return found

    records_for_url = find

    def search(self, query: str = "", *, claim_class: str | None = None) -> list[EvidenceRecord]:
        """Search cached metadata/excerpts without network access."""
        needle = query.casefold()
        found: list[EvidenceRecord] = []
        for path in sorted(self.records_dir.glob("*.json"), key=lambda p: p.name):
            try:
                record = EvidenceRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if claim_class is not None and record.claim_class != claim_class:
                continue
            if needle in f"{record.title}\n{record.source_url}\n{record.excerpt}".casefold():
                found.append(record)
        return found

    cached_search = search

    def cache_content(
        self,
        source_url: str,
        content: str | bytes,
        *,
        excerpt: str | None = None,
        confidence: float = 0.5,
        claim_class: str = "general",
        retrieved_at: str | None = None,
        title: str = "",
    ) -> EvidenceRecord:
        text = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else content
        record = EvidenceRecord.create(source_url, excerpt if excerpt is not None else text, confidence=confidence, claim_class=claim_class, retrieved_at=retrieved_at, content=content, title=title)
        return self.put(record, content)

    def get_or_fetch(
        self,
        source_url: str,
        fetcher: Callable[[str], Any] | None = None,
        *,
        offline: bool = False,
        excerpt: str | None = None,
        confidence: float = 0.5,
        claim_class: str = "general",
        title: str = "",
    ) -> EvidenceRecord:
        """Get cached evidence, or invoke an injected fetcher once online."""
        wanted_hash = _digest(excerpt) if excerpt is not None else None
        candidates = self.find(source_url, excerpt_hash=wanted_hash, claim_class=claim_class)
        if candidates:
            return candidates[0]
        if offline:
            raise OfflineCacheMiss(f"no cached evidence for {source_url}")
        if fetcher is None:
            raise ValueError("fetcher is required for an uncached online lookup")
        result = fetcher(source_url)
        if isinstance(result, EvidenceRecord):
            return self.put(result)
        if isinstance(result, Mapping):
            if "source_url" in result and "retrieved_at" in result:
                return self.put(EvidenceRecord.from_dict(result))
            body = result.get("content", result.get("text", result.get("excerpt")))
            if body is not None:
                return self.cache_content(
                    str(result.get("source_url", source_url)), body,
                    excerpt=str(result.get("excerpt", excerpt)) if result.get("excerpt", excerpt) is not None else None,
                    confidence=float(result.get("confidence", confidence)), claim_class=str(result.get("claim_class", claim_class)), title=str(result.get("title", title)),
                )
            raise TypeError("mapping fetch results require evidence fields or content")
        if not isinstance(result, (str, bytes)):
            raise TypeError("fetcher must return text, bytes, a mapping, or EvidenceRecord")
        return self.cache_content(source_url, result, excerpt=excerpt, confidence=confidence, claim_class=claim_class, title=title)

    def __len__(self) -> int:
        return sum(1 for _ in self.records_dir.glob("*.json"))


__all__ = ["EvidenceCache", "OfflineCacheMiss"]
