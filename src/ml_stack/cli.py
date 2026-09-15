from __future__ import annotations
import argparse, json
from .config import load_settings
from .mcp.registry import Registry
from .mcp.stdio import serve

def main(argv=None):
    raw = list(argv) if argv is not None else __import__("sys").argv[1:]
    if raw and raw[0] == "/ml-stack": raw[0] = "workflow"
    parser = argparse.ArgumentParser(prog="ml-stack", description="Portable ML research and experiment runtime")
    parser.add_argument("command", nargs="?", default="status", choices=["init","status","doctor","mcp","workflow","events"]); parser.add_argument("args", nargs="*")
    ns = parser.parse_args(raw); settings = load_settings(); registry = Registry(settings)
    if ns.command == "mcp": serve(registry); return 0
    if ns.command == "init": result = registry.call("ml_stack.init")
    elif ns.command == "status": result = registry.call("ml_stack.status")
    elif ns.command == "doctor": result = doctor(settings, registry)
    elif ns.command == "events": result = registry.call("ml_stack.events", {"after": int(ns.args[0]) if ns.args else 0})
    else: result = workflow(registry, ns.args)
    print(json.dumps(result, indent=2)); return 0

def workflow(registry, args): return {"workflow":"/ml-stack","input":" ".join(args).strip(),"status":"READY","next":"Use MCP tools or host-native skill selection."}
def doctor(settings, registry):
    settings.ensure_state(); host = settings.host; return {"ok":True,"host":host,"surface":"generic MCP + CLI","slash_command":host in {"claude","claude-code"},"tools":registry.list_tools(),"state_dir":str(settings.state_dir)}
if __name__ == "__main__": raise SystemExit(main())
