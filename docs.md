# ML Stack operator notes

Install with `python -m pip install --editable .`, then run `ml-stack init` and `ml-stack doctor`.

The local stdio MCP transport is `ml-stack mcp`; it emits JSON-RPC responses on stdout. The optional daemon is `ml-stackd --host 127.0.0.1 --port 8787` and exposes `/health` and authenticated `/mcp`. Set `ML_STACK_DAEMON_TOKEN` for bearer authentication. `ML_STACK_*` environment variables configure state and policy; secrets are referenced by name and are never serialized into the ledger.

Promoted artifacts live under `.ml-stack/versions/vN/` and are immutable. Requirements locks are under `.ml-stack/requirements/`; root `requirements.md` is a visible summary unless the compiler is asked to opt out.
