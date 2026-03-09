# Project Scratchpad

Goal: retry the last task

## Acceptance Criteria
### Acceptance Criteria: Retry Last Task

1. **Task Identification:** The system must parse the recent execution history (e.g., `core/HEARTBEAT.md` or `logs/audit.log`) to accurately identify the most recently attempted or failed task.
2. **State Cleansing:** The system must identify and clear any residual state, cached errors, or file locks associated with the previous task attempt to ensure a clean execution environment.
3. **Execution Re-trigger:** The identified task must be automatically re-queued and executed by the appropriate agent or script, preserving its original parameters and environmental constraints.
4. **Execution Monitoring:** The retry process must be monitored, with all standard output and errors captured in a fresh log sequence to prevent mixing with the previous attempt's data.
5. **Completion Verification:** Upon conclusion, the system must update the task's status (Success/Failure) in the core state tracking files and emit a status notification detailing the outcome of the retry.

## Architecture
Here is the finalized, hardened architecture plan for the **Retry Last Task** capability. This design strictly adheres to the security and scalability mandates from the critique while maximizing the **High-Performance (Unlocked)** hardware profile (8 cores, 11.58 GB RAM) through safe concurrency.

### 1. Directory Structure Integration
We will integrate the retry components securely into the `$AGENT_ROOT` structure, enforcing strict file permissions and isolating state to prevent race conditions and privilege escalation.

```text
$AGENT_ROOT/
├── bin/
│   ├── retry_manager.py       # Orchestrator with strict timeout and env whitelisting
│   ├── state_cleanser.py      # Path-traversal-safe cleanup and scoped DB rollbacks
│   └── task_executor.py       # (Existing) Upgraded to write structured state to JSON
├── core/
│   ├── HEARTBEAT.md           # (Existing) High-level source of truth
│   └── task_history.json      # (New) STRICT 0700 PERMS. Sole source of executable truth.
├── logs/
│   ├── audit.log              # (Existing) General logs (NO LONGER PARSED FOR EXECUTION)
│   └── retry_sequences/       # (New) Isolated logs for retry attempts
└── tmp/
    └── retry_locks/           # (New) Secure directory for atomic lock files (0700 perms)
```

### 2. Core Components & Security Fixes

**A. Task State Registry (`core/task_history.json`)**
*   **Function:** Replaces all log parsing. When `task_executor.py` starts a task, it writes a structured JSON object containing `Task_ID`, `Command`, `Args`, `Safe_Env`, and `Registered_Temp_Files`.
*   **Security:** Enforced `0700` permissions. This guarantees that only the AtlasSwarm process can read/write executable parameters, eliminating Log Injection to RCE vulnerabilities.

**B. Task Identifier (`bin/retry_manager.py::TaskIdentifier`)**
*   **Function:** Retrieves the exact parameters of the last failed task by reading *only* from `core/task_history.json`.
*   **Optimization:** High-speed JSON deserialization directly from memory-cached file reads, completely bypassing the CPU-heavy and dangerous regex parsing of unbounded log files.

**C. State Cleanser (`bin/state_cleanser.py`)**
*   **Function:** Safely purges residual state before execution without affecting parallel threads.
*   **Operations:**
    1.  **Cache Safety:** Modifies `bin/cache_utils.py` to use `fcntl.flock(f, fcntl.LOCK_EX)` during reads/writes to `/tmp/api_cache.json`, preventing JSON corruption from race conditions.
    2.  **DB Safety:** Instead of flushing the global `write_queue` in `db_manager.py` (which destroys parallel task data), it executes a task-scoped `ROLLBACK` or deletes specific `Task_ID` records using a dedicated DuckDB connection.
    3.  **File Safety:** Reads `Registered_Temp_Files` from `task_history.json`. Uses `os.path.abspath` and `os.path.commonpath` to strictly verify that every file target resides within `$WORKSPACE` before calling `os.remove()`, eliminating Path Traversal risks.

**D. Execution Re-trigger & Monitor (`bin/retry_manager.py::RetryEngine`)**
*   **Function:** Spawns a dedicated thread for the retry, fully sandboxed.
*   **Operations:**
    1.  **Atomic Locking:** Creates a lock file in `$AGENT_ROOT/tmp/retry_locks/<task_id>.lock` using `os.open(path, os.O_CREAT | os.O_EXCL, 0o600)` to prevent TOCTOU symlink attacks and concurrent retries of the same task.
    2.  **Environment Whitelisting:** Constructs a new environment dictionary containing *only* explicitly whitelisted variables (e.g., `PATH`, `AGENT_ROOT`, `TELEGRAM_USER_ID`). Drops all others to prevent `LD_PRELOAD` or environment hijacking.
    3.  **Timeout Enforcement:** Wraps the thread/subprocess in a strict timeout (e.g., `timeout=300` seconds). If the task hangs, it is aggressively terminated, preventing zombie processes from exhausting the 8-core CPU.
    4.  **Log Isolation:** Pipes `stdout` and `stderr` directly to `logs/retry_sequences/retry_<task_id>_<timestamp>.log`.

**E. Completion Verifier (`bin/retry_manager.py::StatusUpdater`)**
*   **Function:** Monitors execution, updates `HEARTBEAT.md`, and notifies the Telegram gateway asynchronously upon completion or timeout.

### 3. Hardened Data Flow Architecture

```mermaid
1. TRIGGER: Operator sends "/retry" or System detects failure.
   |
   v
2. TASK IDENTIFICATION (TaskIdentifier):
   - Read `core/task_history.json` (Structured JSON, NO log parsing).
   - Extract verified `Task_ID`, `Command`, `Args`, `Safe_Env`, `Registered_Temp_Files`.
   |
   v
3. ATOMIC LOCKING & CLEANSING (StateCleanser):
   - Create lock: `os.open('tmp/retry_locks/<id>.lock', O_CREAT|O_EXCL, 0600)`.
   - Wipe cache entry using `fcntl.flock` for thread safety.
   - Rollback task-scoped DuckDB transactions.
   - Validate and delete `Registered_Temp_Files` (Strict $WORKSPACE boundary check).
   |
   v
4. ISOLATED & TIMED EXECUTION (RetryEngine):
   - Apply Environment Whitelist (Drop unknown vars).
   - Spawn Thread/Subprocess (Max Threads: 8 limit respected).
   - Enforce Hard Timeout (e.g., 300s) to prevent resource exhaustion.
   - Pipe STDOUT/STDERR strictly to `logs/retry_sequences/`.
   |
   v
5. VERIFICATION & CLEANUP (StatusUpdater):
   - Await completion or timeout exception.
   - Release atomic lock file.
   - Rewrite `core/HEARTBEAT.md` status.
   - Emit async notification via `tg_gateway.py`.
```

### 4. Implementation Strategy & Git Protocol

1.  **Branching:** I will create a new branch `feature/secure-task-retry-system` to implement these changes, preserving the `main` branch integrity.
2.  **Conservation Principle:** Existing logging in `logs/audit.log` will remain untouched. `db_manager.py` and `cache_utils.py` will be *upgraded* with scoped connections and `fcntl` locks, respectively, rather than having their existing functionality deleted or disabled.
3.  **Hardware Optimization:** By utilizing thread-safe locks (`fcntl`), atomic file operations (`O_EXCL`), and structured JSON parsing, we achieve maximum I/O throughput and concurrency optimization tailored for the 11.58 GB RAM / 8-Core profile, without the risk of OOM kills from unbounded log parsing.
