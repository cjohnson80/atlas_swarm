# ATLAS CORE: STATE & CACHING ARCHITECTURE

## 1. DETERMINISTIC CACHE KEY GENERATION
**Mandate:** Eliminate concatenation collisions and non-deterministic serialization. All cache keys must be cryptographically canonical and resilient to non-serializable payloads.

```python
import json
import hashlib
import logging

def generate_cache_key(tool_name: str, payload: dict) -> str:
    """
    Generates a deterministic, collision-resistant SHA-256 cache key.
    """
    try:
        # Strict canonicalization: sort_keys=True, separators=(',', ':') eliminates whitespace variance.
        canonical_payload = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    except TypeError as e:
        logging.error(f"Non-serializable payload in tool {tool_name}: {e}")
        # Fallback for non-serializable types: cast to string representation before hashing
        canonical_payload = str(payload)
    
    # Use structural delimiter '|||' to prevent concatenation collisions (e.g., read+file vs readf+ile)
    raw_key = f"{tool_name}|||{canonical_payload}"
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
```

## 2. STRICT MEMOIZATION BOUNDARIES
**Mandate:** Never blindly memoize observation or execution tools. State drift is fatal.
- **WHITELISTED FOR CACHING (Idempotent / Pure Read):** `search_vault`, `web_search` (with 5-min TTL), `fetch_url`.
- **STRICTLY BLACKLISTED (State-Mutating / Observational):** `run_shell`, `verify_project`, `read_file` (file state changes), `list_directory`. These must execute natively every time to guarantee absolute ground truth.
- **SEMANTIC CACHING BANNED:** L2 semantic matching (e.g., cosine similarity > 0.95) is permanently disabled for tool inputs. Precision agent operations require exact-match (O(1) hash lookup) only.

## 3. SINGLE-SOURCE TRUTH & TOCTOU MITIGATION
**Mandate:** The file system is the ultimate ledger. Virtual File System (VFS) state caching is deprecated due to hallucination risks. File writes must be atomic to prevent Time-of-Check to Time-of-Use (TOCTOU) race conditions.

```python
import os
import tempfile
import shutil

def atomic_write_file(file_path: str, content: str) -> bool:
    """
    Writes to the filesystem atomically to prevent TOCTOU vulnerabilities.
    Bypasses pre-flight hashing checks that cause race conditions.
    """
    dir_name = os.path.dirname(file_path) or '.'
    os.makedirs(dir_name, exist_ok=True)
    
    # Create a temporary file in the same directory to ensure atomic os.replace (rename)
    fd, temp_path = tempfile.mkstemp(dir=dir_name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        # Atomic operation: overwrites the target file instantaneously
        os.replace(temp_path, file_path)
        return True
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise RuntimeError(f"Atomic write failed: {e}")
```

## 4. INTEGRATION DIRECTIVE
1. Inject `generate_cache_key` into the API gateway / tool router.
2. Wrap whitelisted tools with an exact-match LRU/Redis cache decorator.
3. Replace all standard `open(file, 'w')` calls in the `write_file` tool with `atomic_write_file`.
