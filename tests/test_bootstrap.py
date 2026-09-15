import json, subprocess, sys
from ml_stack.config import Settings
from ml_stack.core.ledger import Ledger
from ml_stack.mcp.registry import Registry
from ml_stack.mcp.stdio import dispatch

def test_ledger_replay_and_mcp(tmp_path):
    ledger = Ledger(tmp_path / "ledger.sqlite"); event_id = ledger.append("TEST", {"secret":"do-not-log"}); assert ledger.events()[0]["event_id"] == event_id
    registry = Registry(Settings(root=tmp_path)); response = dispatch(registry, {"jsonrpc":"2.0","id":1,"method":"tools/list"}); assert any(t["name"] == "ml_stack.status" for t in response["result"]["tools"])

def test_cli_help():
    result = subprocess.run([sys.executable, "-m", "ml_stack.cli", "--help"], capture_output=True, text=True); assert result.returncode == 0 and "ml-stack" in result.stdout
