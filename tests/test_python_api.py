import csv
import json
from importlib.util import find_spec

from ml_stack import ResearchClient, create_research_client
from ml_stack.research import MemoryResearchAdapter, read_ipynb

def test_python_client_writes_valid_jupyter_artifact(tmp_path):
    adapter = MemoryResearchAdapter({"anchor": [{"source_url": "https://example.test/paper", "title": "Paper", "content": "evidence"}]})
    client = ResearchClient.open(tmp_path, adapter=adapter)
    notebook = tmp_path / "research" / "paper.ipynb"
    result = client.anchor("transformer", limit=1, ipynb_path=notebook)
    parsed = read_ipynb(notebook)
    assert result.records and parsed["nbformat"] == 4
    assert parsed["metadata"]["ml_stack"]["evidence_count"] == 1
    assert any(cell["cell_type"] == "code" for cell in parsed["cells"])
    assert create_research_client(tmp_path, adapter=adapter).cache.root.exists()

def test_dataset_view_is_lazy_and_auditable(tmp_path):
    path = tmp_path / "data.csv"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", "target"]); writer.writeheader(); writer.writerow({"id": "a", "target": "1"})
    view = ResearchClient.open(tmp_path, offline=True).dataset(path, target="target")
    assert view.audit["rows"] == 1 and view.sample(1)[0]["id"] == "a"
    if find_spec("pandas") is not None:
        assert len(view.to_pandas()) == 1


def test_jupyter_line_magic_uses_python_client(tmp_path):
    from ml_stack.jupyter import research_line
    client = ResearchClient.open(tmp_path, adapter=MemoryResearchAdapter({"anchor": [{"source_url": "https://example.test", "content": "ok"}]}))
    namespace = {"ml_client": client}
    result = research_line("transformer --kind anchor --limit 1", namespace=namespace)
    assert namespace["ml_result"] is result and len(result.records) == 1