"""Paper-first research orchestration and source adapter contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Protocol

from ..evidence import EvidenceCache, EvidenceRecord, OfflineCacheMiss
from .notebook import synthesize_notebook, write_notebook

PAPER_FIRST_KINDS = (
    "anchor",
    "recent",
    "citations",
    "method",
    "experiment",
    "code",
    "api",
    "dataset",
)


class ResearchAdapter(Protocol):
    """Read-only adapter used by :class:`PaperFirstResearch`.

    ``search`` returns URL strings or mappings with ``source_url`` and optional
    ``excerpt``, ``content``, ``title``, and ``confidence``. ``fetch`` returns
    source content or such a mapping. Implementations must not mutate a project
    or execute retrieved text.
    """

    def search(self, kind: str, query: str, limit: int) -> Iterable[Any]: ...

    def fetch(self, source_url: str) -> Any: ...


@dataclass(frozen=True, slots=True)
class ResearchRequest:
    query: str
    kinds: tuple[str, ...] = PAPER_FIRST_KINDS
    limit_per_kind: int = 5
    offline: bool = False
    max_context_chars: int = 24_000

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("research query must not be empty")
        unknown = set(self.kinds).difference(PAPER_FIRST_KINDS)
        if unknown:
            raise ValueError(f"unsupported paper-first research kinds: {sorted(unknown)}")
        if self.limit_per_kind < 1 or self.max_context_chars < 1:
            raise ValueError("research request limits must be positive")


@dataclass(slots=True)
class ResearchResult:
    query: str
    records: list[EvidenceRecord] = field(default_factory=list)
    by_kind: dict[str, list[str]] = field(default_factory=dict)
    offline: bool = False

    def notebook(self, title: str | None = None) -> str:
        return synthesize_notebook(self.records, title=title or f"Research: {self.query}")

    def write_notebook(self, path: str) -> str:
        return write_notebook(self.records, path, title=f"Research: {self.query}")

    def citations(self) -> list[str]:
        return [record.source_url for record in sorted(self.records, key=lambda r: r.key)]


class PaperFirstResearch:
    """Run deterministic anchor-to-dataset research over an injected adapter."""

    def __init__(self, cache: EvidenceCache, adapter: ResearchAdapter | None = None):
        self.cache = cache
        self.adapter = adapter

    def collect(
        self,
        query: str | ResearchRequest,
        *,
        adapter: ResearchAdapter | None = None,
        kinds: Iterable[str] | None = None,
        limit_per_kind: int = 5,
        offline: bool = False,
        notebook_path: str | None = None,
    ) -> ResearchResult:
        request = query if isinstance(query, ResearchRequest) else ResearchRequest(
            query=query,
            kinds=tuple(kinds or PAPER_FIRST_KINDS),
            limit_per_kind=limit_per_kind,
            offline=offline,
        )
        source = adapter or self.adapter
        if not request.offline and source is None:
            raise ValueError("an adapter is required for online research")
        records: dict[str, EvidenceRecord] = {}
        by_kind: dict[str, list[str]] = {}
        # This order is normative: broad paper anchors precede implementation
        # and dataset details, avoiding solution-first research.
        for kind in request.kinds:
            kind_records: list[EvidenceRecord] = []
            if request.offline:
                candidates = self.cache.search(request.query, claim_class=f"paper.{kind}")
                # Older cache entries may have a more specific class; URL/text
                # search remains useful offline while retaining stable ordering.
                if not candidates:
                    candidates = self.cache.search(request.query)
                kind_records.extend(candidates[: request.limit_per_kind])
            else:
                references = list(source.search(kind, request.query, request.limit_per_kind))  # type: ignore[union-attr]
                for reference in references:
                    record = self._materialize(reference, kind, source, request.offline)
                    if record is not None:
                        kind_records.append(record)
            ids: list[str] = []
            for record in sorted(kind_records, key=lambda r: r.key):
                records.setdefault(record.key, record)
                ids.append(record.key)
            by_kind[kind] = ids
        result = ResearchResult(request.query, list(records.values()), by_kind, request.offline)
        result.records.sort(key=lambda r: r.key)
        if notebook_path is not None:
            result.write_notebook(notebook_path)
        return result

    research = collect

    # Explicit helpers make paper-first stages discoverable without requiring
    # callers to know the internal kind string.
    def anchor(self, query: str, **kwargs: Any) -> ResearchResult:
        return self.collect(query, kinds=("anchor",), **kwargs)

    def recent(self, query: str, **kwargs: Any) -> ResearchResult:
        return self.collect(query, kinds=("recent",), **kwargs)

    def citations(self, query: str, **kwargs: Any) -> ResearchResult:
        return self.collect(query, kinds=("citations",), **kwargs)

    def method(self, query: str, **kwargs: Any) -> ResearchResult:
        return self.collect(query, kinds=("method",), **kwargs)

    def experiment(self, query: str, **kwargs: Any) -> ResearchResult:
        return self.collect(query, kinds=("experiment",), **kwargs)

    def code(self, query: str, **kwargs: Any) -> ResearchResult:
        return self.collect(query, kinds=("code",), **kwargs)

    def api(self, query: str, **kwargs: Any) -> ResearchResult:
        return self.collect(query, kinds=("api",), **kwargs)

    def dataset(self, query: str, **kwargs: Any) -> ResearchResult:
        return self.collect(query, kinds=("dataset",), **kwargs)

    def _materialize(self, reference: Any, kind: str, source: ResearchAdapter, offline: bool) -> EvidenceRecord | None:
        if isinstance(reference, EvidenceRecord):
            return self.cache.put(reference)
        if isinstance(reference, str):
            fetched = self.cache.get_or_fetch(
                reference,
                source.fetch,
                offline=offline,
                claim_class=f"paper.{kind}",
            )
            return fetched
        if not isinstance(reference, Mapping):
            return None
        url = reference.get("source_url", reference.get("url"))
        if not isinstance(url, str) or not url:
            return None
        content = reference.get("content", reference.get("text"))
        excerpt = reference.get("excerpt")
        title = str(reference.get("title", ""))
        confidence = float(reference.get("confidence", 0.5))
        if content is not None:
            return self.cache.cache_content(url, content, excerpt=str(excerpt) if excerpt is not None else None, confidence=confidence, claim_class=f"paper.{kind}", title=title)
        if excerpt is not None:
            # A search hit with no body is still usable evidence; fetch only if
            # the adapter is online and the cache has no matching hit.
            existing = self.cache.find(url, excerpt_hash=_hash(str(excerpt)), claim_class=f"paper.{kind}")
            if existing:
                return existing[0]
        return self.cache.get_or_fetch(url, source.fetch, offline=offline, excerpt=str(excerpt) if excerpt is not None else None, confidence=confidence, claim_class=f"paper.{kind}", title=title)


def _hash(value: str) -> str:
    import hashlib
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class MemoryResearchAdapter:
    """Small deterministic adapter useful for local/offline integrations."""

    def __init__(self, entries: Mapping[str, Iterable[Any]] | None = None):
        self.entries = {kind: list(values) for kind, values in (entries or {}).items()}
        self.fetched: dict[str, Any] = {}
        for values in self.entries.values():
            for value in values:
                if isinstance(value, Mapping) and isinstance(value.get("source_url", value.get("url")), str):
                    self.fetched.setdefault(value.get("source_url", value.get("url")), value)

    def search(self, kind: str, query: str, limit: int) -> Iterable[Any]:
        values = self.entries.get(kind, [])
        return list(values)[:limit]

    def fetch(self, source_url: str) -> Any:
        if source_url not in self.fetched:
            raise OfflineCacheMiss(f"adapter has no source: {source_url}")
        value = self.fetched[source_url]
        if isinstance(value, Mapping) and "content" in value:
            return value["content"]
        return value


__all__ = ["MemoryResearchAdapter", "PAPER_FIRST_KINDS", "PaperFirstResearch", "ResearchAdapter", "ResearchRequest", "ResearchResult"]
