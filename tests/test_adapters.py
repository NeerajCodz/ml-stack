import json
from pathlib import Path

from ml_stack.adapters import generate


SKILLS = ("ml-stack", "ml-stack-research", "ml-stack-experiment", "ml-stack-audit")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_generate_emits_portable_and_host_native_packages(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "adapters"
    result = generate(root / "skills-src", output)

    portable = output / "openai"
    manifest = read_json(portable / "plugin.json")
    assert manifest["$schema"].endswith("/plugin.schema.json")
    assert manifest["name"] == "ml-stack"
    assert read_json(portable / "mcp.json")["$schema"].endswith("/mcp.schema.json")
    assert read_json(portable / "mcp.json")["mcpServers"]["ml-stack"]["type"] == "stdio"
    assert all((portable / "skills" / skill / "SKILL.md").is_file() for skill in SKILLS)

    claude = output / "claude"
    assert read_json(claude / ".claude-plugin" / "plugin.json")["version"] == "0.2.0"
    assert "mcpServers" in read_json(claude / ".mcp.json")

    opencode = read_json(output / "opencode" / "opencode.json")
    assert opencode["mcp"]["ml-stack"] == {
        "type": "local",
        "command": ["ml-stack", "mcp"],
        "enabled": True,
    }

    marketplace = output / "openai-marketplace" / ".agents" / "plugins" / "marketplace.json"
    entry = read_json(marketplace)["plugins"][0]
    assert entry["source"]["path"] == "./plugins/ml-stack"
    assert (marketplace.parent.parent.parent / "plugins" / "ml-stack" / "plugin.json").is_file()
    assert result["openai_marketplace"].endswith("openai-marketplace")
