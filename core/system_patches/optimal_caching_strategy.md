# ATLAS Core: Optimal Caching Strategy & Single-Source Truth Enforcement

## 1. Deterministic Cache Key Generation
To prevent concatenation collisions and variable whitespace cache misses:
```python
import hashlib
import json

def generate_cache_key(tool_name: str, payload: dict) -> str:
    try:
        # Strict canonicalization: sort_keys and explicit separators
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    except TypeError as e:
        # Reject non-serializable payloads to prevent state drift
        raise ValueError(f"Payload must be JSON serializable: {e}")
    
    # Null-byte delimiter prevents concatenation collisions
    raw_key = f"{tool_name}\x00{payload_str}"
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
```

## 2. Atomic File Operations (TOCTOU & Privilege Escalation Mitigation)
To prevent TOCTOU vulnerabilities, path traversal, and privilege escalation during state updates:
```python
import os
import tempfile
from pathlib import Path

def atomic_write_file(file_path: str, content: str, base_dir: str = ".") -> None:
    base_path = Path(base_dir).resolve()
    # Explicitly join before resolving to preserve CWD-agnostic path resolution
    target_path = base_path.joinpath(file_path).resolve()
    
    # Path traversal protection
    if not target_path.is_relative_to(base_path):
        raise PermissionError("Path traversal detected.")
        
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract existing permissions without TOCTOU exists() check
    target_mode = 0o644
    try:
        target_mode = target_path.stat().st_mode
    except FileNotFoundError:
        pass
        
    fd, temp_path = tempfile.mkstemp(dir=target_path.parent)
    try:
        # fchmod inside fdopen context mitigates inotify symlink privilege escalation
        os.fchmod(fd, target_mode)
        with os.fdopen(fd, 'w') as f:
            f.write(content)
            
        os.replace(temp_path, target_path)
    except Exception as e:
        # Blind removal prevents TOCTOU during cleanup
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise e
```

## 3. Tool-Call Memoization Policy
- **Read-Only Tools:** (e.g., `read_file`, `search_files`) Memoized with TTL and cache invalidation hooks triggered by state-mutating tools.
- **Mutating Tools:** (e.g., `write_file`, `run_shell`) MUST NOT be blindly memoized. They update the centralized state ledger and immediately invalidate dependent cache keys.
- **Semantic Caching:** Strictly forbidden for exact-match diagnostic tools. Reserved only for fuzzy external knowledge retrieval.
