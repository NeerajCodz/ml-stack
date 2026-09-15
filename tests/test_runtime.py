from ml_stack.autonomy import AutonomousLoop, StopPolicy
from ml_stack.core.ledger import Ledger
from ml_stack.core.lifecycle import Operation, OperationKind
from ml_stack.memory import MemoryCard, MemoryStore
from ml_stack.runtime import SessionEngine
from ml_stack.tools import ToolRouter, ToolSpec

def test_session_tool_privacy_and_memory(tmp_path):
    ledger = Ledger(tmp_path / "ledger.sqlite"); session = SessionEngine(ledger).create(); engine = SessionEngine(ledger); engine.sessions[session.session_id] = session
    state = engine.apply(session.session_id, Operation(OperationKind.USER_INPUT, {"text":"hello"})); assert state["state"] == "RUNNING"
    router = ToolRouter(); router.register(ToolSpec("ml_stack.echo", lambda a: a["x"])); assert router.call("ml_stack.echo", {"x": 2}) == 2
    store = MemoryStore(tmp_path / "memory.jsonl"); store.put(MemoryCard("project", "validation", "holdout", ["paper"], .9)); assert store.search("valid")
    assert len(AutonomousLoop(StopPolicy(max_experiments=2)).run(lambda i: {"i":i})) == 2
