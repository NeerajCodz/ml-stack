from __future__ import annotations
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable
from ..schemas import Requirement, RequirementsLock

class RequirementsConflict(ValueError): pass

class RequirementsCompiler:
    def __init__(self, root: Path):
        self.root = root
        self.state = root / ".ml-stack" / "requirements"
        self.state.mkdir(parents=True, exist_ok=True)

    def capture(self, text: str, source: str = "user", confidence: float = 1.0, claim_class: str = "requirement") -> Requirement:
        if not text.strip(): raise ValueError("requirement text cannot be empty")
        rid = hashlib.sha256(text.strip().encode()).hexdigest()[:16]
        return Requirement(text=text.strip(), source=source, confidence=confidence, claim_class=claim_class, requirement_id=rid)

    def compile(self, requirements: Iterable[Requirement], revision: int | None = None, lock: bool = True) -> RequirementsLock:
        items = list(requirements)
        seen: dict[str, Requirement] = {}
        for item in items:
            key = item.text.lower()
            if key in seen and seen[key].source != item.source: raise RequirementsConflict(f"duplicate requirement from conflicting sources: {item.text}")
            seen[key] = item
        if revision is None:
            prior = sorted(self.state.glob("lock-*.json"))
            revision = int(prior[-1].stem.split("-")[1]) + 1 if prior else 1
        payload = [asdict(i) for i in items]
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        result = RequirementsLock(revision=revision, requirements=items, digest=digest)
        if lock:
            output = self.state / f"lock-{revision}.json"
            if output.exists(): raise FileExistsError(f"immutable requirements lock exists: {output}")
            output.write_text(json.dumps({"revision":revision,"requirements":payload,"digest":digest}, indent=2) + "\n", encoding="utf-8")
        return result

    def write_visible(self, lock: RequirementsLock, opt_out_root_write: bool = False) -> Path:
        target = self.state / "user.md" if opt_out_root_write else self.root / "requirements.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Requirements\n\n" + "\n".join(f"- {r.text}" for r in lock.requirements) + "\n", encoding="utf-8")
        if opt_out_root_write:
            (self.root / "requirements.md").write_text("# Requirements\n\nSource: `.ml-stack/requirements/user.md`\n", encoding="utf-8")
        return target
