from __future__ import annotations

from pathlib import Path
from .ledger import Ledger
from ..config import Settings

def initialize(settings: Settings) -> Ledger:
    settings.ensure_state()
    return Ledger(settings.database)
