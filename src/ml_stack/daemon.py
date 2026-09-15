from __future__ import annotations
import argparse, json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .config import load_settings
from .mcp.registry import Registry
from .mcp.stdio import dispatch

class Handler(BaseHTTPRequestHandler):
    registry: Registry | None = None
    token: str | None = None
    def do_GET(self):
        if self.path == "/health": self._send(200, {"ok": True, "service": "ml-stackd"}); return
        self._send(404, {"error":"not found"})
    def do_POST(self):
        if self.path != "/mcp": self._send(404, {"error":"not found"}); return
        origin = self.headers.get("Origin")
        if origin and origin not in {"null", "http://localhost", "https://localhost"}: self._send(403, {"error":"origin rejected"}); return
        if self.token and self.headers.get("Authorization") != f"Bearer {self.token}": self._send(401, {"error":"unauthorized"}); return
        try: request = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0")))); self._send(200, dispatch(self.registry, request))
        except Exception as exc: self._send(400, {"error":str(exc)})
    def _send(self, status, value):
        body = json.dumps(value).encode(); self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *_): pass

def main(argv=None):
    parser = argparse.ArgumentParser(prog="ml-stackd"); parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=8787); args = parser.parse_args(argv)
    Handler.registry = Registry(load_settings()); Handler.token = os.environ.get("ML_STACK_DAEMON_TOKEN")
    server = ThreadingHTTPServer((args.host, args.port), Handler); print(f"ml-stackd listening on http://{args.host}:{args.port}", flush=True); server.serve_forever()
if __name__ == "__main__": main()
