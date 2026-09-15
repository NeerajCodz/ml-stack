from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from ..config import Settings
from ..core.bootstrap import initialize
from ..data import audit_path
from ..discovery import discover_project
from ..requirements import RequirementsCompiler

@dataclass(slots=True)
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], Any]

class Registry:
    def __init__(self, settings: Settings):
        self.settings = settings; self.settings.ensure_state(); self.ledger = initialize(settings); self.tools = self._tools()
    def _tools(self) -> dict[str, Tool]:
        return {
            "ml_stack.status": Tool("ml_stack.status", "Return runtime and ledger status", {"type":"object"}, self._status),
            "ml_stack.init": Tool("ml_stack.init", "Initialize project state", {"type":"object"}, self._init),
            "ml_stack.discover": Tool("ml_stack.discover", "Inventory a project", {"type":"object"}, self._discover),
            "ml_stack.audit_data": Tool("ml_stack.audit_data", "Audit dataset metadata and samples", {"type":"object","properties":{"path":{"type":"string"},"target":{"type":["string","null"]}},"required":["path"]}, self._audit),
            "ml_stack.capture_requirements": Tool("ml_stack.capture_requirements", "Capture and lock explicit requirements", {"type":"object","required":["requirements"],"properties":{"requirements":{"type":"array","items":{"type":"string"}},"opt_out_root_write":{"type":"boolean"}}}, self._requirements),
            "ml_stack.events": Tool("ml_stack.events", "Replay append-only events", {"type":"object","properties":{"after":{"type":"integer"}}}, self._events),
        }
    def list_tools(self): return [{"name":t.name,"description":t.description,"inputSchema":t.input_schema} for t in self.tools.values()]
    def call(self, name: str, arguments: dict[str, Any] | None = None):
        if name not in self.tools: raise KeyError(f"unknown tool: {name}")
        return self.tools[name].handler(arguments or {})
    def _status(self, _): return {"ok":True,"version":"0.1.0","root":str(self.settings.root),"state_dir":str(self.settings.state_dir),"tools":len(self.tools)}
    def _init(self, _): self.settings.ensure_state(); self.ledger.append("PROJECT_INITIALIZED", {"root":str(self.settings.root)}); return self._status({})
    def _discover(self, args): return discover_project(args.get("path", self.settings.root))
    def _audit(self, args): return audit_path(args["path"], args.get("target"))
    def _requirements(self, args):
        compiler = RequirementsCompiler(self.settings.root); items = [compiler.capture(text) for text in args["requirements"]]; lock = compiler.compile(items); target = compiler.write_visible(lock, bool(args.get("opt_out_root_write"))); self.ledger.append("REQUIREMENTS_LOCKED", {"revision":lock.revision,"digest":lock.digest}); return {"revision":lock.revision,"digest":lock.digest,"path":str(target)}
    def _events(self, args): return self.ledger.events(int(args.get("after", 0)))
