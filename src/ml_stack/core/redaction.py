from __future__ import annotations
import re
from typing import Any

_SECRET_NAME = re.compile(r"(?i)(api[_-]?key|token|secret|password|authorization|credential|cookie)")
_SECRET_VALUE = re.compile(r"(?i)(api[_-]?key|token|secret|password|authorization)(\s*[:=]\s*)([^,\s}]+)")

def redact(value: Any) -> Any:
    if isinstance(value, dict): return {k: ("[REDACTED]" if _SECRET_NAME.search(str(k)) else redact(v)) for k,v in value.items()}
    if isinstance(value, list): return [redact(v) for v in value]
    if isinstance(value, str): return _SECRET_VALUE.sub(lambda m:m.group(1)+m.group(2)+"[REDACTED]", value)
    return value
