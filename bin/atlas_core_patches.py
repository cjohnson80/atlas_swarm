import hashlib
import json
import threading
import time
import os
from collections import deque
from typing import Any, Dict, Optional

class SecureFlightController:
    def __init__(self, shard_count: int = os.cpu_count() * 4):
        self.shard_count = shard_count
        self._shards = [{} for _ in range(shard_count)]
        self._locks = [threading.Lock() for _ in range(shard_count)]
        self._process_registry = {} # pid -> (cleanup_fn, expiry)
        self._registry_lock = threading.Lock()

    def _get_shard_index(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % self.shard_count

    def get_canonical_hash(self, tool: str, payload: Any, context_id: str) -> str:
        """Prevents delimiter injection and handles complex payloads via Canonical JSON."""
        canonical_payload = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        raw_string = f"{tool}\0{canonical_payload}\0{context_id}"
        return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

    def register_flight(self, flight_id: str, future: Any, pid: Optional[int] = None):
        idx = self._get_shard_index(flight_id)
        with self._locks[idx]:
            self._shards[idx][flight_id] = future
        if pid:
            with self._registry_lock:
                self._process_registry[pid] = (future, time.time() + 30)

    def clear_flight(self, flight_id: str, pid: Optional[int] = None):
        idx = self._get_shard_index(flight_id)
        with self._locks[idx]:
            self._shards[idx].pop(flight_id, None)
        if pid:
            with self._registry_lock:
                self._process_registry.pop(pid, None)

class DynamicTimeoutManager:
    def __init__(self, window_size: int = 50, alpha: float = 0.2):
        self.latencies = deque(maxlen=window_size)
        self.alpha = alpha
        self.p95_latency = 5.0
        self.is_degraded = False
        self.last_degraded_time = 0
        self._lock = threading.Lock()

    def record_execution(self, duration: float, success: bool):
        with self._lock:
            # Penalize timeouts/failures to prevent poisoning, but cap impact
            val = duration if success else min(duration * 1.5, 30.0)
            self.latencies.append(val)
            if len(self.latencies) > 10:
                sorted_lat = sorted(self.latencies)
                self.p95_latency = sorted_lat[int(len(sorted_lat) * 0.95)]
            
            # Circuit Breaker Logic with Half-Open Recovery
            if self.p95_latency > 25.0:
                self.is_degraded = True
                self.last_degraded_time = time.time()
            elif self.is_degraded and (time.time() - self.last_degraded_time > 60):
                # Attempt recovery after 60s cooldown
                self.is_degraded = False

    def get_timeout(self) -> float:
        with self._lock:
            base = self.p95_latency * 1.5
            return max(2.0, min(base, 30.0))

