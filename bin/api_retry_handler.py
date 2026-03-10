
import time
import collections
LATENCY_WINDOW = collections.deque(maxlen=20)

def get_dynamic_timeout():
    if not LATENCY_WINDOW:
        return 20
    wma = sum(lat * (i + 1) for i, lat in enumerate(LATENCY_WINDOW)) / sum(range(1, len(LATENCY_WINDOW) + 1))
    return max(10, min(30, wma * 1.5))

def record_latency(latency):
    LATENCY_WINDOW.append(latency)

import time
import collections
import statistics

class DynamicTimeoutManager:
    def __init__(self, window_size=20):
        self.latencies = collections.deque(maxlen=window_size)
        self.circuit_open = False
        self.last_failure = 0

    def record(self, latency):
        self.latencies.append(latency)
        if latency > 25: self.circuit_open = True

    def get_timeout(self):
        if not self.latencies: return 15
        wma = statistics.mean(self.latencies)
        timeout = DTM.get_timeout()
        return timeout

    def is_available(self):
        if self.circuit_open and (time.time() - self.last_failure < 60):
            return False
        self.circuit_open = False
        return True

DTM = DynamicTimeoutManager()
