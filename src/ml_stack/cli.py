from __future__ import annotations
import argparse, json
from .config import load_settings
from .mcp.registry import Registry
from .mcp.stdio import serve
from .research import PAPER_FIRST_KINDS, ResearchClient

def main(argv=None):
    raw = list(argv) if argv is not None else __import__("sys").argv[1:]
    if raw and raw[0] == "/ml-stack": raw[0] = "workflow"
    parser = argparse.ArgumentParser(prog="ml-stack", description="Portable ML research and experiment runtime")
    parser.add_argument("command", nargs="?", default="status", choices=["init", "status", "doctor", "mcp", "research", "workflow", "events"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--offline", action="store_true", help="use only cached research evidence")
    parser.add_argument("--kind", action="append", dest="kinds", help="research stage; repeatable")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--max-age", type=float, default=None, dest="max_age_seconds")
    parser.add_argument("--notebook", default=None, help="write deterministic Markdown notebook")
    parser.add_argument("--ipynb", default=None, help="write standard Jupyter notebook")
    ns = parser.parse_args(raw); settings = load_settings(); registry = Registry(settings)
    if ns.command == "mcp": serve(registry); return 0
    if ns.command == "init": result = registry.call("ml_stack.init")
    elif ns.command == "status": result = registry.call("ml_stack.status")
    elif ns.command == "doctor": result = doctor(settings, registry)
    elif ns.command == "events": result = registry.call("ml_stack.events", {"after": int(ns.args[0]) if ns.args else 0})
    elif ns.command == "research": result = research(settings, ns)
    else: result = workflow(registry, ns.args)
    print(json.dumps(result, indent=2)); return 0

def research(settings, ns):
    if not ns.args or not " ".join(ns.args).strip(): raise SystemExit("ml-stack research requires a query")
    result = ResearchClient.from_settings(settings).research(" ".join(ns.args), kinds=tuple(ns.kinds or PAPER_FIRST_KINDS), limit=ns.limit, offline=ns.offline, max_age_seconds=ns.max_age_seconds, notebook_path=ns.notebook, ipynb_path=ns.ipynb)
    return {"query": result.query, "records": len(result.records), "citations": result.citations(), "provenance": result.provenance(), "notebook": ns.notebook, "ipynb": ns.ipynb, "offline": result.offline}

def workflow(registry, args): return {"workflow":"/ml-stack","input":" ".join(args).strip(),"status":"READY","next":"Use MCP tools or host-native skill selection."}
def doctor(settings, registry):
    settings.ensure_state(); host = settings.host; return {"ok":True,"host":host,"surface":"generic MCP + CLI + Python + Jupyter artifacts","slash_command":host in {"claude","claude-code"},"tools":registry.list_tools(),"state_dir":str(settings.state_dir)}
if __name__ == "__main__": raise SystemExit(main())
