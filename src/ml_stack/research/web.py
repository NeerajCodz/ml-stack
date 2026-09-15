"""Read-only, rate-limited adapters for primary research indexes.

The adapters return metadata mappings understood by :class:`PaperFirstResearch`.
Retrieved text is evidence data only; it is never executed or interpreted as policy.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

DEFAULT_ALLOWED_HOSTS = frozenset({
    "export.arxiv.org", "arxiv.org", "api.crossref.org", "api.openalex.org",
    "api.semanticscholar.org", "huggingface.co", "www.huggingface.co",
    "api.github.com", "github.com",
})

class WebResearchError(RuntimeError): pass
class DomainNotAllowed(WebResearchError): pass
class ResponseTooLarge(WebResearchError): pass

@dataclass(slots=True)
class WebClient:
    allowed_hosts: frozenset[str] = DEFAULT_ALLOWED_HOSTS
    timeout: float = 10.0
    max_bytes: int = 2_000_000
    min_interval: float = 0.5
    retries: int = 1
    user_agent: str = "ml-stack-research/0.2 (+https://github.com/NeerajCodz/ml-stack)"
    _last_request: float = 0.0

    def _validate_url(self, url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https":
            raise DomainNotAllowed("research adapters require HTTPS")
        host = (parsed.hostname or "").lower()
        if host not in self.allowed_hosts:
            raise DomainNotAllowed(f"research domain is not allowlisted: {host}")
        return host

    def get(self, url: str, *, accept: str = "application/json") -> tuple[bytes, Mapping[str, str]]:
        self._validate_url(url)
        error: Exception | None = None
        for attempt in range(self.retries + 1):
            delay = self.min_interval - (time.monotonic() - self._last_request)
            if delay > 0: time.sleep(delay)
            request = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": self.user_agent})
            self._last_request = time.monotonic()
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    # Redirects must remain inside the explicit domain policy.
                    self._validate_url(response.geturl())
                    length = response.headers.get("Content-Length")
                    if length and int(length) > self.max_bytes: raise ResponseTooLarge(url)
                    body = response.read(self.max_bytes + 1)
                    if len(body) > self.max_bytes: raise ResponseTooLarge(url)
                    return body, dict(response.headers.items())
            except ResponseTooLarge: raise
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                error = exc
                code = getattr(exc, "code", 0)
                # A provider rate-limit is surfaced immediately. The caller's
                # outer scheduler can retry later without blocking a worker.
                if code == 429:
                    break
                if attempt >= self.retries or (code and code not in {500, 502, 503, 504}):
                    break
                time.sleep(min(2.0 ** attempt, 8.0))
        raise WebResearchError(f"research request failed: {url}: {error}")

    def json(self, url: str) -> Any:
        body, _ = self.get(url, accept="application/json")
        try: return json.loads(body)
        except json.JSONDecodeError as exc: raise WebResearchError(f"invalid JSON from {url}") from exc

class ArxivAdapter:
    base = "https://export.arxiv.org/api/query"
    def __init__(self, client: WebClient | None = None):
        # arXiv documents a three-second request interval; never retry a
        # refused request inside a bounded worker.
        self.client = client or WebClient(timeout=5.0, min_interval=3.0, retries=0)
    def search(self, kind: str, query: str, limit: int) -> Iterable[dict[str, Any]]:
        field = "submittedDate" if kind == "recent" else "relevance"
        params = urllib.parse.urlencode({"search_query": f"all:{query}", "start": 0, "max_results": min(limit, 50), "sortBy": field, "sortOrder": "descending"})
        body, _ = self.client.get(f"{self.base}?{params}", accept="application/atom+xml")
        ns = {"a": "http://www.w3.org/2005/Atom"}; root = ET.fromstring(body)
        for entry in root.findall("a:entry", ns):
            url = (entry.findtext("a:id", "", ns) or "").strip(); title = " ".join((entry.findtext("a:title", "", ns) or "").split()); summary = " ".join((entry.findtext("a:summary", "", ns) or "").split())
            if url:
                url = url.replace("http://", "https://")
                yield {"source_url": url, "title": title, "excerpt": summary, "content": summary, "confidence": 0.8, "source_type": "paper", "retrieval_method": "arxiv_api"}
    def fetch(self, source_url: str) -> str:
        body, _ = self.client.get(source_url, accept="application/atom+xml,text/html"); return body.decode("utf-8", "replace")

class CrossrefAdapter:
    base = "https://api.crossref.org/works"
    def __init__(self, client: WebClient | None = None): self.client = client or WebClient()
    def search(self, kind: str, query: str, limit: int) -> Iterable[dict[str, Any]]:
        params = urllib.parse.urlencode({"query.bibliographic": query, "rows": min(limit, 50), "select": "DOI,title,author,URL,published,abstract"})
        data = self.client.json(f"{self.base}?{params}")
        for item in data.get("message", {}).get("items", []):
            doi = item.get("DOI"); url = item.get("URL") or (f"https://doi.org/{doi}" if doi else "")
            title = (item.get("title") or [""])[0]; abstract = item.get("abstract", "")
            if url: yield {"source_url": url, "title": title, "excerpt": abstract or title, "content": abstract or title, "confidence": 0.75, "source_type": "paper", "retrieval_method": "crossref_api"}
    def fetch(self, source_url: str) -> str: return self.client.get(source_url, accept="text/html,application/json")[0].decode("utf-8", "replace")

class OpenAlexAdapter:
    base = "https://api.openalex.org/works"
    def __init__(self, client: WebClient | None = None): self.client = client or WebClient()
    def search(self, kind: str, query: str, limit: int) -> Iterable[dict[str, Any]]:
        params = urllib.parse.urlencode({"search": query, "per-page": min(limit, 50), "sort": "publication_date:desc" if kind == "recent" else "relevance_score:desc"})
        data = self.client.json(f"{self.base}?{params}")
        for item in data.get("results", []):
            url = item.get("doi") or item.get("primary_location", {}).get("landing_page_url") or item.get("id", ""); title = item.get("title", "")
            if url: yield {"source_url": url, "title": title, "excerpt": title, "content": title, "confidence": 0.7, "source_type": "paper", "retrieval_method": "openalex_api"}
    def fetch(self, source_url: str) -> str: return self.client.get(source_url, accept="text/html,application/json")[0].decode("utf-8", "replace")

class SemanticScholarAdapter:
    base = "https://api.semanticscholar.org/graph/v1"
    def __init__(self, client: WebClient | None = None): self.client = client or WebClient()
    def search(self, kind: str, query: str, limit: int) -> Iterable[dict[str, Any]]:
        params = urllib.parse.urlencode({"query": query, "limit": min(limit, 100), "fields": "title,abstract,url,year,externalIds"})
        data = self.client.json(f"{self.base}/paper/search?{params}")
        for item in data.get("data", []):
            paper_id = item.get("paperId", "")
            url = item.get("url") or (f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else "")
            title = item.get("title", "") or ""
            abstract = item.get("abstract", "") or title
            if url:
                yield {"source_url": url, "title": title, "excerpt": abstract, "content": abstract, "confidence": 0.78, "source_type": "paper", "retrieval_method": "semantic_scholar_api"}
    def fetch(self, source_url: str) -> str:
        return self.client.get(source_url, accept="text/html,application/json")[0].decode("utf-8", "replace")

class GitHubAdapter:
    def __init__(self, client: WebClient | None = None): self.client = client or WebClient()
    def search(self, kind: str, query: str, limit: int) -> Iterable[dict[str, Any]]:
        params = urllib.parse.urlencode({"q": query, "per_page": min(limit, 30), "sort": "stars", "order": "desc"})
        data = self.client.json(f"https://api.github.com/search/repositories?{params}")
        for item in data.get("items", []):
            yield {"source_url": item.get("html_url", ""), "title": item.get("full_name", ""), "excerpt": item.get("description", "") or "", "content": item.get("description", "") or "", "confidence": 0.65, "source_type": "code", "retrieval_method": "github_api"}
    def fetch(self, source_url: str) -> str: return self.client.get(source_url, accept="text/html,application/json")[0].decode("utf-8", "replace")

class HuggingFaceAdapter:
    """Read-only Hub metadata adapter for model and dataset intelligence."""
    base = "https://huggingface.co/api"
    def __init__(self, client: WebClient | None = None): self.client = client or WebClient()
    def search(self, kind: str, query: str, limit: int) -> Iterable[dict[str, Any]]:
        endpoint = "datasets" if kind == "dataset" else "models"
        params = urllib.parse.urlencode({"search": query, "limit": min(limit, 50)})
        data = self.client.json(f"{self.base}/{endpoint}?{params}")
        for item in data if isinstance(data, list) else []:
            identifier = item.get("id", "")
            if not identifier: continue
            url = f"https://huggingface.co/{endpoint[:-1]}/{identifier}"
            text = item.get("pipeline_tag", "") or item.get("description", "") or identifier
            yield {"source_url": url, "title": identifier, "excerpt": text, "content": json.dumps(item, sort_keys=True), "confidence": 0.7, "source_type": "dataset" if endpoint == "datasets" else "model", "retrieval_method": "huggingface_api"}
    def fetch(self, source_url: str) -> str:
        return self.client.get(source_url, accept="text/html,application/json")[0].decode("utf-8", "replace")

class MultiSourceAdapter:
    """Route stages to independent indexes without merging source truth."""
    def __init__(self, adapters: Iterable[Any] | None = None):
        self.adapters = tuple(adapters or (ArxivAdapter(), OpenAlexAdapter(), SemanticScholarAdapter(), CrossrefAdapter(), GitHubAdapter(), HuggingFaceAdapter()))
    def search(self, kind: str, query: str, limit: int) -> Iterable[dict[str, Any]]:
        seen: set[str] = set(); remaining = limit
        ordered = list(self.adapters)
        if kind == "code":
            ordered.sort(key=lambda a: 0 if isinstance(a, GitHubAdapter) else 1)
        elif kind == "dataset":
            ordered.sort(key=lambda a: 0 if isinstance(a, HuggingFaceAdapter) else 1)
        for adapter in ordered:
            if remaining <= 0: break
            try:
                for hit in adapter.search(kind, query, remaining):
                    url = hit.get("source_url", "")
                    if url and url not in seen:
                        seen.add(url); remaining -= 1; yield hit
            except WebResearchError:
                continue
    def fetch(self, source_url: str) -> str:
        for adapter in self.adapters:
            try:
                host = urllib.parse.urlparse(source_url).hostname
                if host in getattr(adapter.client, "allowed_hosts", ()): return adapter.fetch(source_url)
            except WebResearchError: continue
        return WebClient().get(source_url, accept="text/html,application/json")[0].decode("utf-8", "replace")

__all__ = ["ArxivAdapter", "CrossrefAdapter", "DomainNotAllowed", "GitHubAdapter", "HuggingFaceAdapter", "MultiSourceAdapter", "OpenAlexAdapter", "ResponseTooLarge", "SemanticScholarAdapter", "WebClient", "WebResearchError"]

