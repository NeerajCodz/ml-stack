from __future__ import annotations
import json, shutil
from pathlib import Path

SKILLS = ("ml-stack", "ml-stack-research", "ml-stack-experiment", "ml-stack-audit")

def _copy_skills(source: Path, destination: Path) -> None:
    for skill in SKILLS:
        target = destination / skill; target.mkdir(parents=True, exist_ok=True); shutil.copy2(source / skill / "SKILL.md", target / "SKILL.md")

def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

def generate(source: str | Path = "skills-src", output: str | Path = "adapters") -> dict[str, str]:
    source, output = Path(source), Path(output); output.mkdir(parents=True, exist_ok=True); mcp = {"command":"ml-stack","args":["mcp"]}; result = {}
    for host in ("generic", "codex", "claude", "opencode"):
        path = output / host
        if path.exists(): shutil.rmtree(path)
    generic = output / "generic"; _copy_skills(source, generic / "skills"); _write(generic / "mcp.json", {"servers":{"ml-stack":mcp}}); result["generic"] = str(generic)
    codex = output / "codex"; _copy_skills(source, codex / ".agents" / "skills"); _write(codex / ".agents" / "mcp.json", {"servers":{"ml-stack":mcp}}); _write(codex / "marketplace.json", {"skills":list(SKILLS)}); result["codex"] = str(codex)
    claude = output / "claude"; _copy_skills(source, claude / "skills"); _write(claude / ".claude-plugin" / "plugin.json", {"name":"ml-stack","skills":list(SKILLS)}); _write(claude / ".mcp.json", {"mcpServers":{"ml-stack":mcp}}); result["claude"] = str(claude)
    opencode = output / "opencode"; _copy_skills(source, opencode / ".opencode" / "skills"); _write(opencode / "opencode.json", {"mcp":{"ml-stack":mcp}}); result["opencode"] = str(opencode)
    return result
