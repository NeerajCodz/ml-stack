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
