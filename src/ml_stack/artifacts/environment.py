"""Safe runtime environment capture for reproducibility records."""
from __future__ import annotations

import os
import platform
import re
import sys
from typing import Mapping

_SECRET_NAME = re.compile(r"(?:key|token|secret|password|passwd|credential|authorization|cookie)", re.I)


def _safe_environment(values: Mapping[str, str]) -> dict[str, str]:
    return {
        str(name): str(value)
        for name, value in sorted(values.items())
        if not _SECRET_NAME.search(str(name))
    }


def capture_environment(values: Mapping[str, str] | None = None) -> dict[str, object]:
    """Capture interpreter/platform facts without persisting secret values.

    Environment variables are included only when explicitly supplied, making it
    difficult for a normal capture to accidentally copy process credentials.
    """
    result: dict[str, object] = {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "system": platform.system(),
        "executable": sys.executable,
    }
    if values is not None:
        result["environment"] = _safe_environment(values)
    return result


def capture_process_environment() -> dict[str, object]:
    """Explicit opt-in capture of the current process environment."""
    return capture_environment(os.environ)


capture_env = capture_environment
