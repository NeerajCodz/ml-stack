"""Deterministic Markdown notebook rendering for evidence records."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..evidence import EvidenceRecord


def synthesize_notebook(records: Iterable[EvidenceRecord], *, title: str = "Research notebook") -> str:
    """Render evidence into stable Markdown with explicit provenance.

    Records are sorted by their content address and excerpts are fenced as data,
    preventing retrieved Markdown from becoming notebook structure or worker
    instructions. No generation timestamp is added, so equal evidence produces
    byte-for-byte equal notebooks.
    """
    unique = {record.key: record for record in records}
    ordered = [unique[key] for key in sorted(unique)]
    lines = [f"# {_heading(title)}", "", "_Generated from content-addressed evidence._", ""]
    if not ordered:
        lines.append("No evidence records were available.")
        lines.append("")
        return "\n".join(lines)
    for index, record in enumerate(ordered, 1):
        label = record.title.strip() or f"Evidence {index}"
        lines.extend(
            [
                f"## {_heading(label)}",
                "",
                f"- Claim class: `{_inline(record.claim_class)}`",
                f"- Confidence: `{record.confidence:g}`",
                f"- Source: <{record.source_url}>",
                f"- Retrieved: `{_inline(record.retrieved_at)}`",
                f"- Evidence hash: `{record.key}`",
                f"- Excerpt hash: `{record.excerpt_hash}`",
                "",
                "```text",
                record.excerpt.replace("```", "'''"),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def write_notebook(records: Iterable[EvidenceRecord], path: str | Path, *, title: str = "Research notebook") -> str:
    """Write a rendered notebook and return its text."""
    text = synthesize_notebook(records, title=title)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8", newline="\n")
    return text


def _heading(value: str) -> str:
    return " ".join(str(value).replace("\r", " ").replace("\n", " ").split()) or "Research notebook"


def _inline(value: str) -> str:
    return str(value).replace("`", "'").replace("\r", " ").replace("\n", " ")


__all__ = ["synthesize_notebook", "write_notebook"]
