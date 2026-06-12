"""Shared HTTP client and rate limiter for API integrations."""

import hashlib
import json
import time
import threading


class RateLimiter:
    def __init__(self, calls_per_second: float):
        self._min_interval = 1.0 / calls_per_second
        self._lock = threading.Lock()
        self._last = 0.0

    def wait(self):
        with self._lock:
            elapsed = time.monotonic() - self._last
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last = time.monotonic()


def params_hash(*args, **kwargs) -> str:
    raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()
