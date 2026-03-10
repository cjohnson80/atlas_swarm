# ATLAS TECHNICAL BRIEF: CACHING & STATE ENFORCEMENT

## 1. STRATEGIC IMPERATIVES
- **No Blind Memoization:** Observation (`read_file`, `list_directory`) and execution tools (`run_shell`) MUST NOT be memoized. Caching these induces VFS state hallucination and execution blindness.
- **No Semantic Caching for Precision Tools:** L2 semantic caching (e.g., cosine similarity > 0.95) is strictly prohibited for exact-match diagnostic tools to prevent false-positive state retrieval.
- **Deterministic State Ledger:** Cache keys must be cryptographically canonicalized.

## 2. IMPLEMENTATION: DETERMINISTIC CACHE & ATOMIC I/O
The following implementation resolves path traversal, TOCTOU race conditions, privilege escalation, and file descriptor leaks.

```python
import os
import json
import hashlib
import tempfile
import stat
from pathlib import Path
from typing import Any

class DeterministicEncoder(json.JSONEncoder):
    """Ensures deterministic serialization of non-standard types."""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return sorted(list(obj))
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return f"<UNSERIALIZABLE:{type(obj).__name__}>"

def generate_cache_key(tool_name: str, payload: Any) -> str:
    """
    Generates a deterministic, cryptographically secure cache key.
    Uses strict JSON canonicalization and secure delimiters (\x00).
    """
    serialized_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(',', ':'),
        cls=DeterministicEncoder
    )
    raw_key = f"{tool_name}\x00{serialized_payload}"
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

def atomic_write_file(base_dir: str, file_path: str, content: str) -> bool:
    """
    Writes a file atomically.
    Mitigates TOCTOU vulnerabilities, path traversal, and privilege escalation.
    """
    base_path = Path(base_dir).resolve()
    target_path = base_path.joinpath(file_path).resolve()
    
    if not target_path.is_relative_to(base_path):
        raise ValueError("Security Violation: Path traversal detected.")
        
    target_mode = 0o644
    try:
        # Extract and mask permissions to prevent privilege escalation
        target_mode = stat.S_IMODE(target_path.stat().st_mode) & 0o777
    except FileNotFoundError:
        pass

    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    
    fd, temp_path = tempfile.mkstemp(dir=target_dir, prefix=".tmp_")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            # fchmod inside fdopen context prevents fd leak and TOCTOU symlink attacks
            os.fchmod(fd, target_mode)
            f.write(content)
            f.flush()
            os.fsync(fd)
            
        os.replace(temp_path, target_path)
        return True
    except Exception as e:
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise e
```