"""SQLite-authoritative append-only event and record ledger."""
from __future__ import annotations
import hashlib, json, sqlite3, threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from .redaction import redact

def utc_now() -> str: return datetime.now(timezone.utc).isoformat()

class Ledger:
    def __init__(self, path: str | Path): self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True); self._local = threading.local(); self._migrate()
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=30, isolation_level=None); conn.row_factory = sqlite3.Row; conn.execute("PRAGMA journal_mode=WAL"); conn.execute("PRAGMA foreign_keys=ON"); return conn
    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try: yield conn
        finally: conn.close()
    def _migrate(self) -> None:
        with self.connection() as db:
            db.executescript("""CREATE TABLE IF NOT EXISTS migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS events (event_id INTEGER PRIMARY KEY AUTOINCREMENT,event_type TEXT NOT NULL,payload TEXT NOT NULL,created_at TEXT NOT NULL,run_id TEXT); CREATE TABLE IF NOT EXISTS records (namespace TEXT NOT NULL,record_id TEXT NOT NULL,revision INTEGER NOT NULL,payload TEXT NOT NULL,updated_at TEXT NOT NULL,PRIMARY KEY(namespace,record_id)); CREATE TABLE IF NOT EXISTS locks (lock_name TEXT PRIMARY KEY,owner TEXT NOT NULL,acquired_at TEXT NOT NULL,heartbeat_at TEXT NOT NULL);""")
            if not db.execute("SELECT 1 FROM migrations WHERE version=1").fetchone(): db.execute("INSERT INTO migrations VALUES(1, ?)", (utc_now(),))
    def append(self, event_type: str, payload: dict[str, Any], run_id: str | None = None) -> int:
        safe = json.dumps(redact(payload), sort_keys=True, separators=(",", ":"))
        with self.connection() as db: return int(db.execute("INSERT INTO events(event_type,payload,created_at,run_id) VALUES(?,?,?,?)", (event_type, safe, utc_now(), run_id)).lastrowid)
    def events(self, after: int = 0, run_id: str | None = None) -> list[dict[str, Any]]:
        with self.connection() as db: rows = db.execute("SELECT * FROM events WHERE event_id>?" + (" AND run_id=?" if run_id else "") + " ORDER BY event_id", (after, run_id) if run_id else (after,)).fetchall()
        return [{"event_id":r["event_id"],"event_type":r["event_type"],"payload":json.loads(r["payload"]),"created_at":r["created_at"],"run_id":r["run_id"]} for r in rows]
    def put(self, namespace: str, record_id: str, payload: dict[str, Any], expected_revision: int | None = None) -> int:
        now = utc_now(); encoded = json.dumps(redact(payload), sort_keys=True, separators=(",", ":"))
        with self.connection() as db:
            row = db.execute("SELECT revision FROM records WHERE namespace=? AND record_id=?", (namespace, record_id)).fetchone(); current = int(row[0]) if row else 0
            if expected_revision is not None and current != expected_revision: raise ValueError(f"revision conflict: expected {expected_revision}, found {current}")
            revision = current + 1; db.execute("INSERT INTO records VALUES(?,?,?,?,?) ON CONFLICT(namespace,record_id) DO UPDATE SET revision=excluded.revision,payload=excluded.payload,updated_at=excluded.updated_at", (namespace,record_id,revision,encoded,now)); return revision
    def get(self, namespace: str, record_id: str) -> dict[str, Any] | None:
        with self.connection() as db: row = db.execute("SELECT revision,payload,updated_at FROM records WHERE namespace=? AND record_id=?", (namespace, record_id)).fetchone()
        return None if row is None else {"revision":row[0],"payload":json.loads(row[1]),"updated_at":row[2]}
    @staticmethod
    def digest(value: Any) -> str: return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    def acquire(self, lock_name: str, owner: str) -> bool:
        with self.connection() as db:
            try: db.execute("INSERT INTO locks VALUES(?,?,?,?)", (lock_name,owner,utc_now(),utc_now())); return True
            except sqlite3.IntegrityError: return False
    def heartbeat(self, lock_name: str, owner: str) -> None:
        with self.connection() as db:
            if db.execute("UPDATE locks SET heartbeat_at=? WHERE lock_name=? AND owner=?", (utc_now(),lock_name,owner)).rowcount != 1: raise RuntimeError("lock is not owned")
    def release(self, lock_name: str, owner: str) -> None:
        with self.connection() as db: db.execute("DELETE FROM locks WHERE lock_name=? AND owner=?", (lock_name,owner))
