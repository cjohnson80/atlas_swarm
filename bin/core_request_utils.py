import urllib.request
import urllib.error
import json
import time
import ssl
import logging
import random

class CoreRequestManager:
    """
    Centralized Request Manager for the Atlas Swarm.
    Implements Hardened TLS, Exponential Backoff, and Circuit Breaking.
    """
    def __init__(self, timeout=30, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.context = ssl.create_default_context()
        self.context.check_hostname = True
        self.context.verify_mode = ssl.CERT_REQUIRED
        
        # Circuit Breaker State
        self.failure_count = 0
        self.last_failure_time = 0
        self.threshold = 5
        self.cooldown = 60 # seconds

    def _is_circuit_open(self):
        if self.failure_count >= self.threshold:
            if time.time() - self.last_failure_time < self.cooldown:
                return True
            else:
                # Half-Open state for speculative recovery
                return False
        return False

    def request(self, url, data=None, headers=None, method="GET", stream=False):
        if self._is_circuit_open():
            raise RuntimeError("Circuit Breaker Tripped: Swarm I/O is currently throttled.")

        headers = headers or {}
        if data and isinstance(data, dict):
            data = json.dumps(data).encode("utf-8")
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        for attempt in range(self.max_retries):
            try:
                response = urllib.request.urlopen(req, timeout=self.timeout, context=self.context)
                
                # Success - Reset Circuit
                self.failure_count = 0
                
                if stream:
                    return response # Return the raw response object for streaming
                
                with response:
                    res_data = response.read().decode("utf-8")
                    return json.loads(res_data) if "application/json" in response.headers.get("Content-Type", "") else res_data
            
            except urllib.error.HTTPError as e:
                # 4xx errors are usually client-side, don't trip circuit unless it's a 429
                if e.code == 429 or e.code >= 500:
                    self._record_failure()
                
                if attempt == self.max_retries - 1:
                    raise
                
                # Exponential Backoff with Jitter
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)
                
            except (urllib.error.URLError, TimeoutError) as e:
                self._record_failure()
                if attempt == self.max_retries - 1:
                    raise
                time.sleep((2 ** attempt) + random.uniform(0, 1))

    def _record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

# Singleton instance for the core engine
request_manager = CoreRequestManager()
