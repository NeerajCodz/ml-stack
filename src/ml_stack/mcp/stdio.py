from __future__ import annotations
import json, sys
from .registry import Registry

def serve(registry: Registry, stdin=None, stdout=None) -> None:
    stdin = stdin or sys.stdin; stdout = stdout or sys.stdout
    for line in stdin:
        try:
            request = json.loads(line); response = dispatch(registry, request)
        except Exception as exc:
            response = {"jsonrpc":"2.0","id":request.get("id") if isinstance(request, dict) else None,"error":{"code":-32603,"message":str(exc)}}
        stdout.write(json.dumps(response, separators=(",", ":")) + "\n"); stdout.flush()

def dispatch(registry: Registry, request: dict):
    method = request.get("method"); rid = request.get("id")
    if method == "initialize": result = {"protocolVersion":"2025-06-18","capabilities":{"tools":{}},"serverInfo":{"name":"ml-stack","version":"0.1.0"}}
    elif method == "notifications/initialized": return {"jsonrpc":"2.0","id":rid,"result":{}}
    elif method == "tools/list": result = {"tools": registry.list_tools()}
    elif method == "tools/call":
        result = {"content":[{"type":"text","text":json.dumps(registry.call(request["params"]["name"], request["params"].get("arguments", {})))}]}
    else: return {"jsonrpc":"2.0","id":rid,"error":{"code":-32601,"message":f"method not found: {method}"}}
    return {"jsonrpc":"2.0","id":rid,"result":result}
