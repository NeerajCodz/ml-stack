# ML Stack

Portable requirements-driven ML research and experiment runtime.

Install the core package:

```bash
python -m pip install --editable .
```

For notebooks and dataframe workflows:

```bash
python -m pip install --editable '.[notebook,data]'
```

Python API:

```python
from ml_stack.research import ResearchClient

client = ResearchClient.open(".")
result = client.anchor(
    "transformer image classification",
    limit=3,
    ipynb_path="research/transformers.ipynb",
)
print(result.citations())
frame = client.evidence_dataframe(result)  # requires pandas
```

Inside Jupyter, the optional extension provides a direct magic:

```python
%load_ext ml_stack.jupyter
%ml_research transformer image classification --kind anchor --limit 3
ml_result.provenance()
```

The same workflow is available through `ml_stack.research` MCP and `ml-stack research` CLI commands.

## Coding-agent plugins

This project is also a portable plugin for Claude Code, Codex, ChatGPT local
marketplaces, OpenCode, and other MCP/Agent Skills hosts. Install the runtime
with `python -m pip install --editable .`, then follow the complete host-specific
installation guide in [PLUGINS.md](PLUGINS.md). Generated packages are under
`adapters/`; regenerate them with:

```bash
python -c "from ml_stack.adapters import generate; print(generate())"
```
