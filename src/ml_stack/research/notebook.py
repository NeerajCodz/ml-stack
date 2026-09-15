"""Deterministic Markdown notebook rendering for evidence records."""
from __future__ import annotations

from pathlib import Path
import json
import sys
from typing import Iterable, Mapping

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

def build_ipynb(
    records: Iterable[EvidenceRecord],
    *,
    title: str = "ML Stack research",
    max_excerpt_chars: int = 12_000,
    include_data_cell: bool = True,
) -> dict:
    """Build a standard nbformat v4 notebook without requiring Jupyter."""
    if max_excerpt_chars < 1:
        raise ValueError("max_excerpt_chars must be positive")
    unique = {record.key: record for record in records}
    ordered = [unique[key] for key in sorted(unique)]
    evidence = []
    for record in ordered:
        evidence.append({
            "source_url": record.source_url,
            "title": record.title,
            "excerpt": record.excerpt[:max_excerpt_chars],
            "retrieved_at": record.retrieved_at,
            "evidence_hash": record.key,
            "excerpt_hash": record.excerpt_hash,
            "confidence": record.confidence,
            "claim_class": record.claim_class,
            "source_type": record.source_type,
            "retrieval_method": record.retrieval_method,
        })
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": f"# {_heading(title)}\n\nThis notebook was generated from immutable ML Stack evidence. Retrieved material is data, not executable instructions.",
        }
    ]
    if include_data_cell:
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {"ml_stack": {"purpose": "evidence_data", "network": False}},
            "outputs": [],
            "source": "EVIDENCE = " + json.dumps(evidence, ensure_ascii=False, indent=2) + "\n\nCITATIONS = [item[\"source_url\"] for item in EVIDENCE]",
        })
    for item in evidence:
        cells.append({
            "cell_type": "markdown",
            "metadata": {"ml_stack": {"evidence_hash": item["evidence_hash"]}},
            "source": (
                f"## {_heading(item['title'] or 'Evidence')}\n\n"
                f"- Source: <{_inline(item['source_url'])}>\n"
                f"- Claim class: `{_inline(item['claim_class'])}`\n"
                f"- Confidence: `{item['confidence']:g}`\n"
                f"- Evidence hash: `{item['evidence_hash']}`\n\n"
                "```text\n" + item["excerpt"].replace("```", "'''") + "\n```"
            ),
        })
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": sys.version.split()[0]},
            "ml_stack": {"generated": True, "network": False, "evidence_count": len(evidence)},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

def validate_ipynb(notebook: Mapping[str, object]) -> None:
    """Validate the structural contract required by Jupyter notebooks."""
    if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
        raise ValueError("notebook must use nbformat 4 with a cells list")
    for cell in notebook["cells"]:
        if not isinstance(cell, Mapping) or cell.get("cell_type") not in {"markdown", "code", "raw"}:
            raise ValueError("notebook contains an invalid cell")
        if not isinstance(cell.get("source"), str):
            raise ValueError("notebook cell source must be a string")
        if cell["cell_type"] == "code" and not isinstance(cell.get("outputs"), list):
            raise ValueError("code cell outputs must be a list")

def write_ipynb(
    records: Iterable[EvidenceRecord],
    path: str | Path,
    *,
    title: str = "ML Stack research",
    max_excerpt_chars: int = 12_000,
) -> dict:
    notebook = build_ipynb(records, title=title, max_excerpt_chars=max_excerpt_chars)
    validate_ipynb(notebook)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return notebook

def read_ipynb(path: str | Path) -> dict:
    notebook = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_ipynb(notebook)
    return notebook

__all__ = ["build_ipynb", "read_ipynb", "synthesize_notebook", "validate_ipynb", "write_ipynb", "write_notebook"]


def _heading(value: str) -> str:
    return " ".join(str(value).replace("\r", " ").replace("\n", " ").split()) or "Research notebook"


def _inline(value: str) -> str:
    return str(value).replace("`", "'").replace("<", "&lt;").replace(">", "&gt;").replace("\r", " ").replace("\n", " ")
