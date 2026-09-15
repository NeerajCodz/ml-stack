from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    handler: Callable[[dict[str, Any]], Any]
    mutating: bool = False
    requires_approval: bool = False

class ToolRouter:
    def __init__(self): self._tools: dict[str, ToolSpec] = {}
    def register(self, spec: ToolSpec) -> None:
        if not spec.name.startswith("ml_stack."): raise ValueError("tool names must use ml_stack.* namespace")
        if spec.name in self._tools: raise ValueError(f"duplicate tool: {spec.name}")
        self._tools[spec.name] = spec
    def list(self): return [{"name": s.name, "mutating": s.mutating, "requiresApproval": s.requires_approval} for s in self._tools.values()]
    def call(self, name: str, arguments: dict[str, Any], approved: bool = False):
        spec = self._tools.get(name)
        if spec is None: raise KeyError(name)
        if spec.requires_approval and not approved: raise PermissionError(f"approval required for {name}")
        return spec.handler(arguments)
