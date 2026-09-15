from __future__ import annotations
from dataclasses import dataclass
from ..config import Settings
from ..mcp.registry import Registry

@dataclass(slots=True)
class Service:
    settings: Settings
    registry: Registry
    def health(self): return {"ok": True, "service": "ml-stack", "state_dir": str(self.settings.state_dir)}
    def call(self, tool: str, arguments=None): return self.registry.call(tool, arguments or {})
