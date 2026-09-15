"""Evidence records and stable content-addressed identifiers.

Evidence is treated as data: fields are descriptive metadata and excerpts, never
instructions to the caller or to research workers.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping


def _sha256(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """A provenance-bearing claim excerpt.

    ``record_id`` is derived from source and content, not retrieval time or
    confidence. This means that fetching the same source again reuses the same
    cache object while preserving the first observed retrieval timestamp.
    """

    source_url: str
    retrieved_at: str
    excerpt: str
    excerpt_hash: str
    confidence: float
    claim_class: str
    content_hash: str = ""
    title: str = ""
    record_id: str = ""
    schema_version: str = "1.0"
    source_type: str = "web"
    retrieval_method: str = "http"

    def __post_init__(self) -> None:
        if not self.source_url or not isinstance(self.source_url, str):
            raise ValueError("source_url must be a non-empty string")
        if not isinstance(self.excerpt, str):
            raise TypeError("excerpt must be text")
        expected_excerpt_hash = _sha256(self.excerpt)
        if self.excerpt_hash and self.excerpt_hash != expected_excerpt_hash:
            raise ValueError("excerpt_hash does not match excerpt")
        object.__setattr__(self, "excerpt_hash", expected_excerpt_hash)
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.claim_class or not isinstance(self.claim_class, str):
            raise ValueError("claim_class must be a non-empty string")
        try:
            datetime.fromisoformat(self.retrieved_at.replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc:
            raise ValueError("retrieved_at must be an ISO-8601 timestamp") from exc
        if self.content_hash and len(self.content_hash) != 64:
            raise ValueError("content_hash must be a SHA-256 hex digest")

    @classmethod
    def create(
        cls,
        source_url: str,
        excerpt: str,
        *,
        confidence: float = 0.5,
        claim_class: str = "general",
        retrieved_at: str | None = None,
        content: str | bytes | None = None,
        title: str = "",
        source_type: str = "web",
        retrieval_method: str = "http",
    ) -> "EvidenceRecord":
        content_hash = ""
        if content is not None:
            content_hash = _sha256(content)
        return cls(
            source_url=source_url,
            retrieved_at=retrieved_at or _utc_now(),
            excerpt=excerpt,
            excerpt_hash=_sha256(excerpt),
            confidence=float(confidence),
            claim_class=claim_class,
            content_hash=content_hash,
            title=title,
            source_type=source_type,
            retrieval_method=retrieval_method,
        )

    @property
    def identity(self) -> dict[str, str]:
        """The fields used for the stable content-addressed record key."""
        return {
            "source_url": self.source_url,
            "excerpt_hash": self.excerpt_hash,
            "claim_class": self.claim_class,
            "content_hash": self.content_hash,
        }

    @property
    def key(self) -> str:
        return _sha256(_canonical(self.identity))

    def as_dict(self) -> dict[str, Any]:
        result = {
            "schema_version": self.schema_version,
            "record_id": self.record_id or self.key,
            "source_url": self.source_url,
            "retrieved_at": self.retrieved_at,
            "excerpt": self.excerpt,
            "excerpt_hash": self.excerpt_hash,
            "confidence": self.confidence,
            "claim_class": self.claim_class,
            "content_hash": self.content_hash,
            "title": self.title,
            "source_type": self.source_type,
            "retrieval_method": self.retrieval_method,
        }
        return result

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "EvidenceRecord":
        record = cls(
            source_url=str(value["source_url"]),
            retrieved_at=str(value["retrieved_at"]),
            excerpt=str(value.get("excerpt", "")),
            excerpt_hash=str(value.get("excerpt_hash", "")),
            confidence=float(value.get("confidence", 0.5)),
            claim_class=str(value.get("claim_class", "general")),
            content_hash=str(value.get("content_hash", "")),
            title=str(value.get("title", "")),
            record_id=str(value.get("record_id", "")),
            schema_version=str(value.get("schema_version", "1.0")),
            source_type=str(value.get("source_type", "web")),
            retrieval_method=str(value.get("retrieval_method", "http")),
        )
        if record.record_id and record.record_id != record.key:
            raise ValueError("record_id does not match content-addressed identity")
        return record

    def with_record_id(self) -> "EvidenceRecord":
        return EvidenceRecord.from_dict({**self.as_dict(), "record_id": self.key})


__all__ = ["EvidenceRecord"]
