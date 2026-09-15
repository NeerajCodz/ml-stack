from __future__ import annotations

import json
import shutil
from pathlib import Path

SKILLS = ("ml-stack", "ml-stack-research", "ml-stack-experiment", "ml-stack-audit")
PLUGIN_NAME = "ml-stack"
PLUGIN_VERSION = "0.2.0"
PLUGIN_DESCRIPTION = "Requirements-driven ML research, experiments, validation, and evidence audit for coding agents."
AUTHOR = {"name": "ML Stack contributors", "url": "https://github.com/NeerajCodz/ml-stack"}
PORTABLE_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _copy_skills(source: Path, destination: Path, *, openai_overlay: bool = False) -> None:
    for skill in SKILLS:
        target = destination / skill
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / skill / "SKILL.md", target / "SKILL.md")
        if openai_overlay:
            _write(target / "agents" / "openai.yaml", {
                "interface": {
                    "display_name": skill.replace("-", " ").title(),
                    "short_description": f"Use {skill} for the ML Stack workflow.",
                    "default_prompt": f"Use ${skill} to run the ML Stack {skill} workflow.",
                },
                "policy": {"allow_implicit_invocation": True},
            })


def _manifest() -> dict:
    return {
        "$schema": PORTABLE_SCHEMA,
        "name": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "description": PLUGIN_DESCRIPTION,
        "author": AUTHOR,
        "homepage": "https://github.com/NeerajCodz/ml-stack",
        "repository": "https://github.com/NeerajCodz/ml-stack",
        "license": "MIT",
        "keywords": ["machine-learning", "research", "experiments", "mcp", "agents"],
        "extensions": {"com.openai": {"display_name": "ML Stack", "category": "Developer tools"}},
    }


def _portable_mcp() -> dict:
    return {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
        "mcpServers": {"ml-stack": {"type": "stdio", "command": "ml-stack", "args": ["mcp"]}},
    }

def _claude_mcp() -> dict:
    return {"mcpServers": {"ml-stack": {"command": "ml-stack", "args": ["mcp"]}}}


def _clean(output: Path) -> None:
    for host in ("generic", "openai", "codex", "claude", "claude-marketplace", "opencode", "openai-marketplace"):
        path = output / host
        if path.exists(): shutil.rmtree(path)


def generate(source: str | Path = "skills-src", output: str | Path = "adapters") -> dict[str, str]:
    """Generate installable host packages from the canonical Agent Skills tree."""
    source, output = Path(source), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    _clean(output)

    generic = output / "generic"
    _copy_skills(source, generic / "skills")
    _write(generic / "plugin.json", _manifest())
    _write(generic / "mcp.json", _portable_mcp())

    openai = output / "openai"
    _copy_skills(source, openai / "skills", openai_overlay=True)
    _write(openai / "plugin.json", _manifest())
    _write(openai / "mcp.json", _portable_mcp())
    _write(openai / ".codex-plugin" / "plugin.json", {**_manifest(), "skills": "./skills/", "mcp": "./mcp.json"})

    codex = output / "codex"
    _copy_skills(source, codex / ".agents" / "skills", openai_overlay=True)
    _write(codex / ".agents" / "mcp.json", _portable_mcp())
    _write(codex / "marketplace.json", {"name": "ml-stack-local", "plugins": [{"name": PLUGIN_NAME, "source": {"source": "local", "path": "../openai"}}]})

    claude = output / "claude"

    openai_marketplace = output / "openai-marketplace"
    (openai_marketplace / ".agents" / "plugins").mkdir(parents=True, exist_ok=True)
    (openai_marketplace / "plugins").mkdir(parents=True, exist_ok=True)
    shutil.copytree(openai, openai_marketplace / "plugins" / PLUGIN_NAME)
    _write(openai_marketplace / ".agents" / "plugins" / "marketplace.json", {
        "name": "ml-stack-local",
        "plugins": [{
            "name": PLUGIN_NAME,
            "source": {"source": "local", "path": "./plugins/ml-stack"},
            "interface": {"displayName": "ML Stack", "shortDescription": PLUGIN_DESCRIPTION},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Developer tools",
        }],
    })
    _copy_skills(source, claude / "skills")
    _write(claude / ".claude-plugin" / "plugin.json", {"name": PLUGIN_NAME, "description": PLUGIN_DESCRIPTION, "version": PLUGIN_VERSION, "author": AUTHOR, "repository": AUTHOR["url"], "license": "MIT"})
    _write(claude / ".mcp.json", _claude_mcp())
    claude_marketplace = output / "claude-marketplace"
    (claude_marketplace / "plugins").mkdir(parents=True, exist_ok=True)
    shutil.copytree(claude, claude_marketplace / "plugins" / PLUGIN_NAME)
    _write(claude_marketplace / ".claude-plugin" / "marketplace.json", {"name": "ml-stack-local", "owner": AUTHOR, "plugins": [{"name": PLUGIN_NAME, "source": "./plugins/ml-stack"}]})

    opencode = output / "opencode"
    _copy_skills(source, opencode / ".opencode" / "skills")
    _write(opencode / "opencode.json", {"$schema": "https://opencode.ai/config.json", "mcp": {"ml-stack": {"type": "local", "command": ["ml-stack", "mcp"], "enabled": True}}})

    return {"generic": str(generic), "openai": str(openai), "openai_marketplace": str(openai_marketplace), "codex": str(codex), "claude": str(claude), "claude_marketplace": str(claude_marketplace), "opencode": str(opencode)}
