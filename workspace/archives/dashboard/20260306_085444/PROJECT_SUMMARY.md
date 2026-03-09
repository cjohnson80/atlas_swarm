# Project Scratchpad

Goal: start

## Acceptance Criteria
### Acceptance Criteria

- **AC1: Environment Validation**
  - The system verifies the existence of all critical paths within `$AGENT_ROOT` (e.g., `bin/`, `core/`, `logs/`, `workspace/`, `mailbox/`).
  - Missing non-critical directories are automatically created.

- **AC2: Configuration & Hardware Profile Loading**
  - The system successfully reads `local_config.json` (or probes defaults) and confirms the `high-performance` profile is active.
  - Multi-threading is enabled with a maximum of 8 threads.
  - The `db_validator` and `legacy_io_operations` features are confirmed to be disabled.

- **AC3: Core Services Initialization**
  - The core engine (`$AGENT_ROOT/bin/atlas_core.py`) initializes successfully without throwing fatal exceptions.
  - The Telegram Gateway (`$AGENT_ROOT/bin/tg_gateway.py`) starts and successfully binds to the configured Telegram bot token.

- **AC4: Heartbeat & Logging Activation**
  - The async logger (`logger_setup.py`) is initialized and begins writing to `logs/audit.log`.
  - The system reads `core/HEARTBEAT.md` and successfully executes its first heartbeat cycle.

- **AC5: Health Check & System Responsiveness**
  - The system passes a local health check verifying that the core processes are active.
  - The Telegram Gateway is responsive to authorized user commands (e.g., `/start` or `/status`).

## Architecture
Here is the finalized, refined architecture plan for the AtlasSwarm environment. This revision explicitly resolves the identified security vulnerabilities, scalability bottlenecks, and error-handling deficiencies while strictly adhering to the **High-Performance (8-Core)** hardware profile.

---

### 1. Hardened Security Posture (Resolving AC Vulnerabilities)

*   **Strict Command Execution & Sandboxing:**
    *   **Vulnerability Resolved:** Command Injection & Bypassed Blacklists.
    *   **Implementation:** The `is_safe_command` blacklist is deprecated. It is replaced by a strict **Command Allowlist**. Only predefined, parameterized functions mapped to specific intents are permitted. 
    *   **Subprocess Hardening:** All instances of `shell=True` in `tg_gateway.py` and `atlas_core.py` are strictly prohibited. External calls will use parameterized lists (e.g., `subprocess.run(["git", "commit", "-m", f"Mailbox: command for {target_name}"])`). Target names and dynamic inputs will be strictly validated against a whitelist regex (`^[a-zA-Z0-9_-]+$`).
*   **Ephemeral Message Brokering (Deprecating Git Mailbox):**
    *   **Vulnerability Resolved:** Information Disclosure via Git History.
    *   **Implementation:** The `mailbox/` directory will no longer be synced via Git commits. Inter-node communication will transition to a secure, ephemeral broker (e.g., Redis Pub/Sub, MQTT, or a localized encrypted SQLite/DuckDB table with strict TTLs). This ensures sensitive payloads and API keys are never permanently written to version control.

### 2. Scalable Execution & Resource Management (High-Performance Alignment)

*   **Asynchronous I/O & Thread Pool Protection:**
    *   **Bottleneck Resolved:** Thread Pool Exhaustion.
    *   **Implementation:** The 8-thread pool managed by `atlas_core.py` is reserved *exclusively* for CPU-bound tasks. All network-bound tasks (API calls, remote node polling, Telegram updates) will utilize Python's `asyncio` event loop. This prevents long-polling operations from starving the primary worker threads.
*   **Event-Driven Telemetry:**
    *   **Bottleneck Resolved:** Git-Backed Polling Abuse.
    *   **Implementation:** The synchronous 5-second `git pull` polling loop is eliminated. The system will rely on an event-driven architecture (e.g., WebSockets or local sockets) to notify the Telegram Gateway of task completion, reducing disk I/O and network overhead to near zero.
*   **Thread-Safe Database Transactions:**
    *   **Bottleneck Resolved:** Concurrent Database Writes (DuckDB Locking).
    *   **Implementation:** Direct `duckdb.connect()` write calls from the 8 worker threads are architecturally forbidden. All database mutations must be routed through the `DatabaseManager.write_queue` defined in `db_manager.py`. This ensures a single, dedicated background thread handles all writes sequentially, preventing `database is locked` exceptions while allowing concurrent reads.

### 3. Resilient Error Handling & State Management

*   **Active Process Supervision:**
    *   **Deficiency Resolved:** Silent Gateway Failures.
    *   **Implementation:** `tg_gateway.py` will no longer be spawned as an unmonitored subprocess. `atlas_core.py` will implement an `asyncio` watchdog/supervisor loop (or utilize a process manager like `pm2`/`systemd`). If the Telegram gateway exits unexpectedly, the supervisor will capture the exit code, log the stack trace to `logs/atlas_core.log`, and automatically restart the service with exponential backoff.
*   **Deterministic Task State & Dead Letter Queue (DLQ):**
    *   **Deficiency Resolved:** Zombie Task States in Heartbeat.
    *   **Implementation:** The `error_handler.py` will no longer silently return `None`. Tasks parsed from `HEARTBEAT.md` will transition through strict states: `- [ ]` (Pending), `- [IN_PROGRESS]`, `- [x]` (Completed), and `- [FAILED]`. If a task throws an exception, the handler will explicitly mark it as `- [FAILED]` in the markdown file and route the task payload to a Dead Letter Queue (DLQ) database table for manual operator audit.

### 4. Directory & Configuration State (Finalized)

The directory structure remains segregated by concern, but the configuration strictly enforces the hardware profile:

```text
$AGENT_ROOT/
├── bin/              # Core executables (atlas_core.py, tg_gateway.py, db_manager.py)
├── core/             
│   ├── local_config.json # Enforces: max_threads: 8, disabled_features: ["db_validator", "legacy_io_operations"]
│   ├── HEARTBEAT.md  # Strict state tracking (- [ ], - [IN_PROGRESS], - [x], - [FAILED])
│   └── SOUL.md       # Identity and hardware constraints
├── logs/             # Async telemetry (audit.log, atlas_core.log)
├── workspace/        # Transient execution space
└── data/             # Persistent storage (Routed strictly via db_manager.py)
```

### Execution Authorization
This architecture is secure, highly scalable, and fully utilizes the 8-core, 11.58 GB RAM hardware profile while gracefully handling errors. 

Ready to initiate the refactoring of `tg_gateway.py`, `atlas_core.py`, and `error_handler.py` to align with this final specification upon your command.
