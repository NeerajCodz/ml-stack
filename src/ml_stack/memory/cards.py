from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass(slots=True)
class MemoryCard:
    scope: str
    topic: str
    content: str
    evidence: list[str]
    confidence: float
    card_id: str = ""
    created_at: str = ""
    def seal(self):
        self.created_at = self.created_at or datetime.now(timezone.utc).isoformat(); self.card_id = hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()[:20]; return self

class MemoryStore:
    def __init__(self, path): self.path = path; self.path.parent.mkdir(parents=True, exist_ok=True)
    def put(self, card: MemoryCard):
        if card.scope not in {"project", "workspace", "global"}: raise ValueError("invalid memory scope")
        if not card.card_id: card.seal()
        with self.path.open("a", encoding="utf-8") as stream: stream.write(json.dumps(asdict(card), sort_keys=True) + "\n")
        return card
    def search(self, topic: str, scope: str | None = None):
        if not self.path.exists(): return []
        rows = [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return [r for r in rows if topic.lower() in r["topic"].lower() and (scope is None or r["scope"] == scope)]
