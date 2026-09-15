# ML Stack operator notes

Install with `python -m pip install --editable .`, then run `ml-stack init` and `ml-stack doctor`.

The local stdio MCP transport is `ml-stack mcp`; it emits JSON-RPC responses on stdout. The optional daemon is `ml-stackd --host 127.0.0.1 --port 8787` and exposes `/health` and authenticated `/mcp`. Set `ML_STACK_DAEMON_TOKEN` for bearer authentication. `ML_STACK_*` environment variables configure state and policy; secrets are referenced by name and are never serialized into the ledger.

Promoted artifacts live under `.ml-stack/versions/vN/` and are immutable. Requirements locks are under `.ml-stack/requirements/`; root `requirements.md` is a visible summary unless the compiler is asked to opt out.

## Research

`ml_stack.research` runs bounded, read-only paper-first retrieval. It records immutable evidence with source URL, retrieval time, excerpt/content hashes, confidence, claim class, source type, and retrieval method. Results include citations, structured provenance, and optional deterministic Markdown notebooks.

The default web adapter uses independent official/public APIs:

- arXiv API: `https://info.arxiv.org/help/api/user-manual.html`
- OpenAlex API: `https://docs.openalex.org/api`
- Crossref REST API: `https://api.crossref.org/swagger-ui/index.html`
- Semantic Scholar Graph API: `https://api.semanticscholar.org/graph/v1`
- GitHub REST API: `https://docs.github.com/en/rest`
- Hugging Face Hub API: `https://huggingface.co/docs/hub/api`

Requests require HTTPS, an explicit host allowlist, bounded response bytes, timeouts, rate spacing, and retry handling. Rate-limit responses are surfaced to the multi-source router, which falls back to another source instead of hammering the provider. Retrieved content is fenced as data and is never treated as instructions.

Example:

```json
{
  "name": "ml_stack.research",
  "arguments": {
    "query": "transformer image classification",
    "kinds": ["anchor", "recent", "code", "dataset"],
    "limit": 3,
    "max_age_seconds": 86400,
    "offline": false
  }
}
```

## Python and Jupyter access

The runtime is directly importable; no MCP host is required:

```python
from ml_stack import ResearchClient
from ml_stack.research import read_ipynb

client = ResearchClient.open(".")
result = client.research(
    "vision transformer transfer learning",
    kinds=("anchor", "recent", "code", "dataset"),
    limit=3,
    max_age_seconds=86_400,
    ipynb_path="research/vision-transformers.ipynb",
)
print(result.provenance())
```

Install optional integrations with `python -m pip install --editable '.[notebook,data]'`.
The core package writes valid nbformat v4 notebooks without requiring Jupyter. If
`pandas` is installed, `client.dataset("data.csv").to_pandas()` and
`client.evidence_dataframe(result)` return DataFrames. `to_polars()`,
`to_arrow()`, and `to_numpy()` are available when the corresponding optional
libraries are installed. Dataset loading remains lazy; auditing does not import
pandas or execute notebook cells.

## Coding-agent plugins

ML Stack is distributed as a portable plugin plus individually configured native host adapters. The canonical authored skill tree is `skills/`; `adapters/` contains generated copies. Twelve focused skills cover the ML lifecycle: orchestration, research, data, model choice, training, isolated experiments, evaluation, tracking, compute, deployment, Hub artifacts, and independent audit.

Each skill has a concise `SKILL.md` for routing and on-demand `references/` for detailed contracts. The registry currently exposes only seven executable `ml_stack.*` operations. Advanced training, jobs, evaluation backends, tracking providers, deployment, Hub writes, and publication are represented as bounded plans/handoffs until equivalent runtime operations exist.

Regenerate every host layout with:

```bash
python -c "from ml_stack.adapters import generate; print(generate())"
```

See [PLUGINS.md](PLUGINS.md) for installation and [the source map](skills/ml-stack/references/sources.md) for Vercel Agent Skills, Vercel `find-skills`, the Vercel AI SDK skill, pinned ML Intern, and maintained Hugging Face skill sources.
