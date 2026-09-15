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

| `adapters/openai/` | Portable Agent Plugins, Codex, and ChatGPT local marketplaces | Root `plugin.json`, root `mcp.json`, `skills/`, OpenAI skill overlays, and `.codex-plugin/plugin.json` compatibility metadata. |
| `adapters/claude/` | Claude Code | `.claude-plugin/plugin.json`, `skills/`, and `.mcp.json`. |
| `adapters/claude-marketplace/` | Claude Code local marketplace | A marketplace catalog pointing at the generated Claude plugin. |
| `adapters/codex/` | Direct Codex project setup | `.agents/skills/`, a portable MCP fragment, and a local marketplace example. |
| `adapters/opencode/` | OpenCode | `.opencode/skills/` and a native `opencode.json` MCP entry. |
| `adapters/omp/` | OMP native project setup | `.omp/skills/` and `.omp/mcp.json`. |
| `adapters/omp-plugin/` | OMP installable plugin package | `package.json` with `omp` metadata, `skills/`, and `.mcp.json`. |
| `adapters/omp-marketplace/` | OMP local marketplace | `.omp-plugin/marketplace.json` and an installable plugin copy. |
| `adapters/cursor/` | Cursor | `.cursor/skills/` and `.cursor/mcp.json`. |
| `adapters/cline/` | Cline | `.cline/skills/` and `.cline/mcp.json`. |
| `adapters/windsurf/` | Windsurf Cascade | `.windsurf/skills/` and a native `mcp_config.json` fragment. |
| `adapters/gemini/` | Gemini CLI | `.gemini/skills/` and `.gemini/settings.json`. |
| `adapters/github-copilot/` | GitHub Copilot | `.github/skills/`; MCP must be configured on the Copilot/IDE surface. |
| `adapters/vscode/` | VS Code Agent/Copilot | `.github/skills/` and `.vscode/mcp.json`. |
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
## OMP / Oh My Pi

OMP has both a native project layout and an installable plugin layout. Use the
native adapter when configuring one repository:

```bash
mkdir -p .omp/skills
cp -R adapters/omp/.omp/skills/. .omp/skills/
cp adapters/omp/.omp/mcp.json .omp/mcp.json
omp mcp list
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force .omp\skills | Out-Null
Copy-Item -Recurse -Force adapters\omp\.omp\skills\* .omp\skills\
Copy-Item -Force adapters\omp\.omp\mcp.json .omp\mcp.json
omp mcp list
```

For OMP plugin installation, add the generated local marketplace and install
the project plugin:

```bash
omp plugin marketplace add ./adapters/omp-marketplace
omp plugin install --scope project ml-stack@ml-stack-local
omp plugin list
```

OMP discovers skills from `.omp/skills/<name>/SKILL.md` and native MCP servers
from `.omp/mcp.json`. Invoke a skill with `/skill:ml-stack-research`. The
generated OMP MCP file uses OMP's own schema and keeps the server enabled
without sharing secrets.

## Cursor

Copy the native Cursor adapter into the repository:

```bash
mkdir -p .cursor/skills
cp -R adapters/cursor/.cursor/skills/. .cursor/skills/
cp adapters/cursor/.cursor/mcp.json .cursor/mcp.json
```

Cursor discovers `.cursor/skills/<name>/SKILL.md` and reads the
`mcpServers.ml-stack` entry from `.cursor/mcp.json`. Use `/ml-stack-research`
or let Cursor select the skill from its description.

## Cline

Use the project-scoped Cline adapter:

```bash
mkdir -p .cline/skills
cp -R adapters/cline/.cline/skills/. .cline/skills/
cp adapters/cline/.cline/mcp.json .cline/mcp.json
```

Enable Skills in Cline's feature settings, then use the Cline MCP panel or
`cline mcp` to inspect the `ml-stack` server. The Cline-specific MCP fields
(`disabled` and `autoApprove`) are intentionally emitted instead of reusing
Claude or Codex configuration.

## Windsurf Cascade

Copy the workspace skills:

```bash
mkdir -p .windsurf/skills
cp -R adapters/windsurf/.windsurf/skills/. .windsurf/skills/
```

Windsurf's legacy Cascade MCP configuration is user-scoped. Merge
`adapters/windsurf/mcp_config.json` into
`~/.codeium/windsurf/mcp_config.json`, or use **Cascade → MCPs**. Do not
overwrite other servers in that file. Invoke a skill with `@ml-stack-research`
or let Cascade select it by description.

## Gemini CLI

Copy the project skills and merge the generated settings:

```bash
mkdir -p .gemini/skills
cp -R adapters/gemini/.gemini/skills/. .gemini/skills/
```

Merge `adapters/gemini/.gemini/settings.json` into the project's
`.gemini/settings.json`; preserve unrelated settings. The generated file
enables Skills and registers `mcpServers.ml-stack`. Verify with:

```bash
gemini skills list --all
gemini mcp list
```

## GitHub Copilot and VS Code

GitHub Copilot's portable repository skill location is `.github/skills/`:

```bash
mkdir -p .github/skills
cp -R adapters/github-copilot/.github/skills/. .github/skills/
```

GitHub Copilot cloud agent and code review use repository-configured MCP
tools; they do not launch this local stdio command. Use a public HTTPS MCP
deployment for those surfaces. Copilot CLI and IDE surfaces can use a local
MCP connection where their host allows it.

For VS Code Agent/Copilot, copy the same skills and merge the workspace MCP
configuration:

```bash
cp -R adapters/vscode/.github/skills/. .github/skills/
mkdir -p .vscode
cp adapters/vscode/.vscode/mcp.json .vscode/mcp.json
```

VS Code workspace MCP uses a top-level `servers` object, unlike portable
Agent Plugins and Claude's `mcpServers` object. Keep the generated shape when
editing `.vscode/mcp.json`.


## Other coding agents and generic MCP clients

Use `adapters/generic/` when the host supports the Agent Skills convention and a local stdio MCP registration:

1. Copy `adapters/generic/skills/<name>/SKILL.md` into the host's project or user skill directory.
2. Register the server from `adapters/generic/mcp.json`, preserving its `mcpServers.ml-stack` entry.
3. If the host supports portable Agent Plugins, install the entire `adapters/generic/` directory and keep `plugin.json`, `mcp.json`, and `skills/` at its root.
4. If the host has its own MCP configuration, translate only the server entry: executable `ml-stack`, argument `mcp`, stdio transport. Keep host-specific keys and schemas.

Do not assume slash-command syntax is portable. Skills, MCP, Python, and Jupyter are separate integration surfaces; use the host's documented skill invocation and MCP registration commands.

## Official host references

These adapters follow the host-native contracts current at generation time:

- [Agent Plugins](https://developers.openai.com/plugins/build/plugins) and [MCP schema](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json)
- [Claude Code plugins](https://code.claude.com/docs/en/plugins), [Claude discovery](https://code.claude.com/docs/en/discover-plugins), and [Claude MCP](https://code.claude.com/docs/en/mcp)
- [OpenCode plugins](https://opencode.ai/v2/docs/plugins), [skills](https://opencode.ai/v2/docs/skills), and [MCP](https://opencode.ai/v2/docs/mcp-servers)
- [OMP skills](https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md), [OMP plugins](https://github.com/can1357/oh-my-pi/blob/main/docs/plugin-manager-installer-plumbing.md), and [OMP MCP](https://github.com/can1357/oh-my-pi/blob/main/docs/mcp-config.md)
- [Cursor skills](https://prod.cursor.com/docs/skills) and [Cursor MCP](https://prod.cursor.com/docs/mcp)
- [Cline skills](https://docs.cline.bot/customization/skills) and [Cline MCP](https://docs.cline.bot/mcp/mcp-overview)
- [Windsurf skills](https://docs.windsurf.com/windsurf/cascade/skills) and [Windsurf MCP](https://docs.windsurf.com/windsurf/cascade/mcp)
- [Gemini CLI skills](https://geminicli.com/docs/cli/skills/) and [Gemini MCP](https://geminicli.com/docs/tools/mcp-server/)
- [GitHub Copilot agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [VS Code agent skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), [agent plugins](https://code.visualstudio.com/docs/agent-customization/agent-plugins), and [MCP](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)

## Verification

After installation, verify the runtime and generated artifacts:

```bash
ml-stack doctor
python -m pytest -q
python -m compileall -q src tests
```

A host-specific smoke check should show the skill files and parse the generated JSON. For MCP connectivity, use the host's server list/status command (`claude mcp list`, `codex mcp list`, or the OpenCode MCP status view) and approve project-scoped servers when prompted.
