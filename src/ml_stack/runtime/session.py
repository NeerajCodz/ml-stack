from __future__ import annotations
import uuid
from dataclasses import dataclass
from ..core.lifecycle import Operation, OperationKind
from ..core.ledger import Ledger

@dataclass(slots=True)
class Session:
    session_id: str
    last_event_id: int = 0
    state: str = "READY"

class SessionEngine:
    def __init__(self, ledger: Ledger): self.ledger = ledger; self.sessions: dict[str, Session] = {}
    def create(self) -> Session:
        session = Session(uuid.uuid4().hex); self.sessions[session.session_id] = session; self.ledger.append("SESSION_CREATED", {"session_id":session.session_id}, run_id=session.session_id); return session
    def apply(self, session_id: str, operation: Operation) -> dict:
        session = self.sessions.get(session_id) or Session(session_id); self.sessions[session_id] = session
        if operation.kind == OperationKind.SHUTDOWN: session.state = "SHUTDOWN"
        elif operation.kind == OperationKind.COMPACT: session.state = "COMPACTING"
        elif operation.kind == OperationKind.RESUME: session.state = "READY"
        elif operation.kind == OperationKind.USER_INPUT: session.state = "RUNNING"
        event = self.ledger.append("SESSION_OPERATION", {"session_id":session_id,"kind":operation.kind.value,"payload":operation.payload}, run_id=session_id); session.last_event_id = event
        return {"session_id":session_id,"state":session.state,"event_id":event}
    def replay(self, session_id: str, after: int = 0): return self.ledger.events(after, session_id)
