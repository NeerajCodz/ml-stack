"""Bounded read-only research worker with explicit tool policy."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Callable, Iterable, Mapping

from ..evidence import EvidenceRecord


READ_ONLY_TOOLS = frozenset(
    {
        "paper.anchor",
        "paper.recent",
        "paper.citations",
        "paper.method",
        "paper.experiment",
        "paper.code",
        "paper.api",
        "paper.dataset",
        "hf.docs.search",
        "hf.docs.fetch",
        "hf.changelog",
        "web.search",
        "web.open",
        "web.follow",
        "github.repo",
        "github.file",
        "github.issue",
        "github.pull_request",
        "dataset.inspect",
    }
)


class ToolNotAllowed(PermissionError):
    """Raised before a tool outside the worker's read-only allowlist runs."""


class ToolNotAvailable(LookupError):
    """Raised when a permitted tool has no configured implementation."""


class IterationLimitExceeded(RuntimeError):
    """Raised when a worker exceeds its bounded iteration budget."""


class ContextLimitExceeded(RuntimeError):
    """Raised when tool output exceeds the worker context ceiling."""


@dataclass(frozen=True, slots=True)
class ToolAllowlist:
    """Exact and prefix-based allowlist for worker tools.

    Wildcards are suffix-only (for example ``paper.*``). There is no implicit
    wildcard and mutating-looking names are rejected even when a broad prefix
    was accidentally supplied.
    """

    allowed: frozenset[str] = READ_ONLY_TOOLS

    def permits(self, name: str) -> bool:
        if not isinstance(name, str) or not name:
            return False
        if _looks_mutating(name):
            return False
        return name in self.allowed or any(
            entry.endswith(".*") and name.startswith(entry[:-1]) for entry in self.allowed
        )

    def check(self, name: str) -> None:
        if not self.permits(name):
            raise ToolNotAllowed(f"research worker tool is not allowed: {name}")


@dataclass(frozen=True, slots=True)
class ResearchAction:
    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WorkerResult:
    """Stable worker output; trace omits arguments and retrieved text."""

    records: list[EvidenceRecord] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    context_chars: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "records": [record.as_dict() for record in sorted(self.records, key=lambda r: r.key)],
            "trace": list(self.trace),
            "iterations": self.iterations,
            "context_chars": self.context_chars,
        }


class ReadOnlyResearchWorker:
    """Execute injected research handlers under strict bounds.

    Handlers receive a fresh argument dictionary and may only return data. The
    worker never evaluates returned strings as prompts or instructions, never
    writes project files, and never submits compute jobs.
    """

    def __init__(
        self,
        handlers: Mapping[str, Callable[[dict[str, Any]], Any]] | None = None,
        *,
        allowlist: ToolAllowlist | Iterable[str] | None = None,
        max_iterations: int = 8,
        max_context_chars: int = 24_000,
    ):
        if max_iterations < 1 or max_context_chars < 1:
            raise ValueError("worker ceilings must be positive")
        self.handlers = dict(handlers or {})
        if allowlist is None:
            self.allowlist = ToolAllowlist()
        elif isinstance(allowlist, ToolAllowlist):
            self.allowlist = allowlist
        else:
            self.allowlist = ToolAllowlist(frozenset(allowlist))
        self.max_iterations = int(max_iterations)
        self.max_context_chars = int(max_context_chars)

    def execute(self, actions: Iterable[ResearchAction | Mapping[str, Any] | tuple[str, Mapping[str, Any]]]) -> WorkerResult:
        normalized = [_action(value) for value in actions]
        if len(normalized) > self.max_iterations:
            raise IterationLimitExceeded(
                f"research worker limit is {self.max_iterations} iterations, requested {len(normalized)}"
            )
        output = WorkerResult()
        seen: set[str] = set()
        for index, action in enumerate(normalized, 1):
            self.allowlist.check(action.tool)
            handler = self.handlers.get(action.tool)
            if handler is None:
                raise ToolNotAvailable(f"no handler configured for allowed tool: {action.tool}")
            result = handler(dict(action.arguments))
            encoded = json.dumps(_safe_data(result), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            output.context_chars += len(encoded)
            if output.context_chars > self.max_context_chars:
                raise ContextLimitExceeded(
                    f"research worker context exceeds {self.max_context_chars} characters"
                )
            records = _records(result)
            for record in records:
                if record.key not in seen:
                    output.records.append(record)
                    seen.add(record.key)
            output.trace.append({"iteration": index, "tool": action.tool, "record_ids": [r.key for r in records]})
        output.iterations = len(normalized)
        output.records.sort(key=lambda r: r.key)
        return output

    run = execute


def _action(value: ResearchAction | Mapping[str, Any] | tuple[str, Mapping[str, Any]]) -> ResearchAction:
    if isinstance(value, ResearchAction):
        return value
    if isinstance(value, tuple) and len(value) == 2:
        return ResearchAction(str(value[0]), dict(value[1]))
    if isinstance(value, Mapping):
        tool = value.get("tool", value.get("name"))
        if not isinstance(tool, str):
            raise ValueError("research action requires a tool name")
        args = value.get("arguments", value.get("args", {}))
        if not isinstance(args, Mapping):
            raise TypeError("research action arguments must be a mapping")
        return ResearchAction(tool, dict(args))
    raise TypeError("research actions must be ResearchAction, mapping, or (tool, arguments)")


def _looks_mutating(name: str) -> bool:
    lower = name.casefold()
    return any(word in lower.split(".") for word in ("write", "delete", "publish", "submit", "compute", "upload", "stage", "run", "execute", "mutate"))


def _safe_data(value: Any) -> Any:
    if isinstance(value, EvidenceRecord):
        return value.as_dict()
    if isinstance(value, Mapping):
        return {str(key): _safe_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_data(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _records(value: Any) -> list[EvidenceRecord]:
    if isinstance(value, EvidenceRecord):
        return [value]
    if isinstance(value, Mapping):
        if "records" in value and isinstance(value["records"], (list, tuple)):
            return [record for item in value["records"] for record in _records(item)]
        if "source_url" in value:
            try:
                return [EvidenceRecord.from_dict(value)]
            except (KeyError, TypeError, ValueError):
                return []
        return []
    if isinstance(value, (list, tuple)):
        return [record for item in value for record in _records(item)]
    return []


# The shorter name is convenient for callers and preserves the explicit class
# name for code that wants to signal the read-only boundary.
ResearchWorker = ReadOnlyResearchWorker

__all__ = [
    "ContextLimitExceeded",
    "IterationLimitExceeded",
    "READ_ONLY_TOOLS",
    "ResearchAction",
    "ResearchWorker",
    "ReadOnlyResearchWorker",
    "ToolAllowlist",
    "ToolNotAllowed",
    "ToolNotAvailable",
    "WorkerResult",
]
