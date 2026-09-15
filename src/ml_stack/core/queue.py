from __future__ import annotations

import queue
import threading
from .lifecycle import Operation

class OperationQueue:
    def __init__(self) -> None:
        self._queue: queue.Queue[Operation] = queue.Queue()
        self._stop = threading.Event()

    def put(self, operation: Operation) -> None:
        if self._stop.is_set(): raise RuntimeError("operation queue stopped")
        self._queue.put(operation)

    def get(self, timeout: float | None = None) -> Operation:
        return self._queue.get(timeout=timeout)

    def shutdown(self) -> None:
        self._stop.set()

    @property
    def stopped(self) -> bool:
        return self._stop.is_set()
