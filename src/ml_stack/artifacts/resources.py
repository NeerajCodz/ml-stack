"""Conservative host resource capture.

Unknown values stay ``None`` rather than being guessed.  In particular, this
module never claims a GPU is present or that a provider has free capacity.
"""
from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path


def capture_resources(path: str | Path = ".") -> dict[str, object]:
    result: dict[str, object] = {
        "cpu_count": os.cpu_count(),
        "memory_bytes": None,
        "gpu": None,
        "system": platform.system(),
        "machine": platform.machine(),
    }
    try:
        usage = shutil.disk_usage(Path(path))
    except OSError:
        pass
    else:
        result["disk"] = {
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
        }
    # resource is Unix-only and reports process limits, not host capacity.
    try:
        import resource  # type: ignore
    except ImportError:
        return result
    try:
        result["process_max_rss"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (AttributeError, OSError, ValueError):
        pass
    return result


capture_resource_profile = capture_resources
