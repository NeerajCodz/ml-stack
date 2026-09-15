from __future__ import annotations
import json
from ..core.redaction import redact

class PrivacyLedger:
    def __init__(self, ledger): self.ledger = ledger
    def record(self, event_type: str, payload: dict, *, store_trace: bool = False):
        safe = redact(payload); safe = safe if store_trace else {"summary": "trace storage disabled", "keys": sorted(safe)}
        return self.ledger.append(event_type, safe)
