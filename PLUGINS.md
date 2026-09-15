# ML Stack plugins and host installation

ML Stack is a portable coding-agent plugin package. It contains four Agent Skills and one local stdio MCP server:

- Skills: `ml-stack`, `ml-stack-research`, `ml-stack-experiment`, and `ml-stack-audit`.
- MCP server: `ml-stack mcp`.
- Python/Jupyter API: optional; no agent host is required for direct Python use.

The canonical skill sources are under `skills-src/`. Host packages under `adapters/` are generated artifacts. Regenerate them after changing a skill or the adapter generator:

```bash
python -c "from ml_stack.adapters import generate; print(generate())"
```

## Prerequisite: install the runtime

Every local MCP installation needs the `ml-stack` executable on the host's `PATH`:

```bash
python -m pip install --editable .
ml-stack init
ml-stack doctor
```

Use a virtual environment when possible. The generated MCP configurations intentionally contain no API keys or tokens. Configure provider credentials through the normal `ML_STACK_*` environment variables or the host's environment.

## Generated packages

| Package | Host | Contents |
| --- | --- | --- |
| `adapters/openai/` | Portable Agent Plugins, Codex, and ChatGPT local marketplaces | Root `plugin.json`, root `mcp.json`, `skills/`, OpenAI skill overlays, and `.codex-plugin/plugin.json` compatibility metadata. |
| `adapters/claude/` | Claude Code | `.claude-plugin/plugin.json`, `skills/`, and `.mcp.json`. |
| `adapters/claude-marketplace/` | Claude Code local marketplace | A marketplace catalog pointing at the generated Claude plugin. |
| `adapters/codex/` | Direct Codex project setup | `.agents/skills/`, a portable MCP fragment, and a local marketplace example. |
| `adapters/opencode/` | OpenCode | `.opencode/skills/` and a native `opencode.json` MCP entry. |
| `adapters/generic/` | Other Agent Skills-compatible hosts | Portable `plugin.json`, `mcp.json`, and `skills/`. |

The portable Agent Plugins files are deliberately different from Claude's `.mcp.json` and OpenCode's `opencode.json`. Do not rename one host's configuration and expect another host to parse it.

## Claude Code

### Test or use from a local checkout

Claude Code loads a local plugin directory directly:

```bash
claude --plugin-dir ./adapters/claude
```

The generated plugin has the required Claude layout: `.claude-plugin/plugin.json` at the plugin root, with `skills/` and `.mcp.json` beside it. Skills are namespaced by the plugin name:

```text
/ml-stack:ml-stack
/ml-stack:ml-stack-research
/ml-stack:ml-stack-experiment
/ml-stack:ml-stack-audit
```

The bundled MCP server starts as `ml-stack mcp`. Check it from another terminal with:

```bash
claude mcp list
```

### Install through a local Claude marketplace

The generated marketplace is usable without publishing a repository:

```text
/plugin marketplace add ./adapters/claude-marketplace
/plugin install ml-stack@ml-stack-local
```

Choose user, project, or local scope in the plugin manager. For a published marketplace, replace the local path with its Git URL or `owner/repository` and use the marketplace's actual name.

## Codex and portable Agent Plugins

`adapters/openai/` follows the portable Agent Plugins layout. Keep these paths at the plugin root:

```text
plugin.json
mcp.json
skills/
```

The root `mcp.json` uses the Agent Plugins schema and declares the local stdio transport explicitly. The `.codex-plugin/plugin.json` file is only a compatibility fallback; it is not a replacement for the portable root manifest.

### Direct project setup

For a repository-local Codex setup, copy the generated skills into the repository and register the MCP server with Codex:

```powershell
New-Item -ItemType Directory -Force .agents\skills | Out-Null
Copy-Item -Recurse -Force adapters\codex\.agents\skills\* .agents\skills\
codex mcp add ml-stack -- ml-stack mcp
codex mcp list
```

The equivalent POSIX commands are:

```bash
mkdir -p .agents/skills
cp -R adapters/codex/.agents/skills/. .agents/skills/
codex mcp add ml-stack -- ml-stack mcp
codex mcp list
```

Codex stores this server in its user or project `config.toml`; the command is safer than hand-editing that file. The copied `.agents/skills/` tree is the native Codex project skill location.

### Portable plugin marketplace

The generated marketplace can be registered with the Codex CLI:

```bash
codex plugin marketplace add ./adapters/openai-marketplace
codex plugin marketplace list
```

For a repository or team marketplace, commit a marketplace catalog under `.agents/plugins/marketplace.json` and point its plugin source at a `./`-prefixed relative path containing `adapters/openai/`. Use the ChatGPT desktop Plugins Directory or Codex's plugin UI to install the package from that marketplace.

## ChatGPT

The portable Agent Plugins package is the ChatGPT-compatible package. ChatGPT and Codex share the public plugin directory, but local filesystem access is not available to a hosted ChatGPT conversation.

For local development, register `adapters/openai-marketplace/` as a local marketplace with the Codex CLI, restart the ChatGPT desktop app, then install **ML Stack** from the Plugins Directory. The local stdio server still requires the Python package to be installed on the same machine.

For a hosted/public ChatGPT plugin, `ml-stack mcp` must be deployed behind a public HTTPS MCP endpoint and registered through ChatGPT developer mode. Do not paste a local `ml-stack` command into a hosted ChatGPT connection; it cannot launch a process on your workstation. Public plugin submission and authentication belong to the MCP deployment, not this repository's local adapter.

## OpenCode

OpenCode uses native skills and MCP configuration rather than the Agent Plugins or Claude plugin manifest:

```bash
mkdir -p .opencode/skills
cp -R adapters/opencode/.opencode/skills/. .opencode/skills/
```

Merge the generated `adapters/opencode/opencode.json` `mcp.ml-stack` object into the project's existing `opencode.json`; do not overwrite unrelated settings. The generated entry is:

```json
{
  "mcp": {
    "ml-stack": {
      "type": "local",
      "command": ["ml-stack", "mcp"],
      "enabled": true
    }
  }
}
```

OpenCode discovers the four skills from `.opencode/skills/<name>/SKILL.md`. Ask OpenCode to use a skill by its name; Claude's `/ml-stack:<name>` namespace is not an OpenCode command.

## Other coding agents and generic MCP clients

Use `adapters/generic/` when the host supports the Agent Skills convention and a local stdio MCP registration:

1. Copy `adapters/generic/skills/<name>/SKILL.md` into the host's project or user skill directory.
2. Register the server from `adapters/generic/mcp.json`, preserving its `mcpServers.ml-stack` entry.
3. If the host supports portable Agent Plugins, install the entire `adapters/generic/` directory and keep `plugin.json`, `mcp.json`, and `skills/` at its root.
4. If the host has its own MCP configuration, translate only the server entry: executable `ml-stack`, argument `mcp`, stdio transport. Keep host-specific keys and schemas.

Do not assume slash-command syntax is portable. Skills, MCP, Python, and Jupyter are separate integration surfaces; use the host's documented skill invocation and MCP registration commands.

## Verification

After installation, verify the runtime and generated artifacts:

```bash
ml-stack doctor
python -m pytest -q
python -m compileall -q src tests
```

A host-specific smoke check should show the skill files and parse the generated JSON. For MCP connectivity, use the host's server list/status command (`claude mcp list`, `codex mcp list`, or the OpenCode MCP status view) and approve project-scoped servers when prompted.
