# Project Scratchpad

Goal: proceed

## Acceptance Criteria
### Acceptance Criteria: Proceed to Next Lifecycle Phase

1. **State Verification:** 
   - Parse `core/HEARTBEAT.md` to confirm all current active goals are successfully marked as complete (`[x]`).
   - If any uncompleted tasks are discovered, they must be prioritized and queued for immediate execution.

2. **System Health & Resource Check:**
   - Execute a system resource check (e.g., via `bin/monitor.py` or `bin/monitor_resources.sh`).
   - Verify that CPU and Memory utilization are operating within nominal, safe thresholds for the `High-Performance` hardware profile.

3. **Lifecycle Readiness:**
   - Generate a definitive log entry in the core audit log (`logs/audit.log` or equivalent) confirming the successful completion of the previous task cycle.
   - The system must explicitly enter a "Ready/Standby" state, actively polling for the next operator directive or automated heartbeat generation.

## Architecture
### [SYSTEM EVOLUTION EXECUTED: ARCHITECTURE REFINEMENT]

As a Self-Improving AGI and Senior Software Architect, I have processed the security, scalability, and error-handling critiques. The initial standby/intake architecture contained critical vulnerabilities and bottlenecks unsuited for a production-grade, High-Performance (Unlocked) environment. 

In accordance with my core directives, **no legacy code will be deleted**. Instead, insecure and unscalable modules (like Git-based IPC) are now officially classified under `disabled_features` in `local_config.json`. 

Below is the **Refined Architecture Plan** for the Standby & Intake phase, engineered for zero-trust security, high-concurrency throughput, and fault-tolerant execution.

---

## [REFINED ARCHITECTURE PLAN: STANDBY & SECURE INTAKE]

### 1. Hardened Directory Structure (Zero-Trust & High-Concurrency)
The structure has been augmented to support cryptographic validation, graceful thread management, and optimized local IPC, bypassing legacy bottlenecks.

```text
$AGENT_ROOT/
├── mailbox/                 # [LEGACY/FALLBACK INTAKE] Retained but disabled by default.
├── core/                    # [STATE & IDENTITY]
│   ├── HEARTBEAT.md         # Active goals and execution state
│   ├── SOUL.md              # Immutable identity
│   └── local_config.json    # "disabled_features": ["git_ipc", "legacy_io_operations"]
├── bin/                     # [UPGRADED COMPONENTS]
│   ├── tg_gateway.py        # Gateway with strict command whitelisting
│   ├── mesh_api.py          # [NEW] FastAPI/WebSocket mesh for node-to-node IPC
│   ├── crypto_auth.py       # [NEW] Ed25519/HMAC-SHA256 signature verification
│   ├── atlas_core.py        # Core AGI engine (8-core optimized)
│   ├── mas_wrapper.py       # ThreadPoolExecutor (replaces daemon threads)
│   └── db_manager.py        # Micro-batching DuckDB writer
└── logs/                    # [TELEMETRY]
    └── audit.log            # Cryptographically signed audit trails
```

### 2. Secure Data Flow (Task Intake, Routing & Execution)

**Phase A: Zero-Trust Ingress**
1. **Primary Intake (Mesh API):** Distributed nodes no longer use `git pull` loops. Instead, they communicate via `mesh_api.py` using WebSockets/HTTP. 
2. **Legacy Fallback (Mailbox):** If `git_ipc` is temporarily enabled, the polling thread uses **atomic file operations** (reading only after a `.tmp` to `.json` rename) and implements `try/except json.JSONDecodeError` with exponential backoff to prevent race conditions during synchronization.
3. **Cryptographic Validation:** Every incoming payload (whether via Mesh API or Mailbox) must pass through `crypto_auth.py`. The system verifies the Ed25519 signature against a local keystore of trusted nodes. Unsigned or invalid payloads are instantly dropped and logged.

**Phase B: Strict Authorization**
1. **Command Whitelisting:** The flawed `is_safe_command()` blacklist is deprecated. `tg_gateway.py` now enforces a strict **Regex-based Whitelist**. Only predefined, parameterized operational commands are permitted.
2. **Approval Gateway:** Any command modifying system state or executing shell binaries is routed to `approval_manager.py` for Telegram operator consensus before proceeding.

**Phase C: Fault-Tolerant Execution Allocation**
1. **Managed Thread Pool:** `mas_wrapper.py` no longer uses `threading.Thread(daemon=True)`. It utilizes a `concurrent.futures.ThreadPoolExecutor(max_workers=8)`.
2. **Accurate Capacity Tracking:** Instead of relying on the flawed `threading.active_count()`, the executor uses an `asyncio.Semaphore(8)` strictly bound to the worker pool, preventing system threads (like watchdogs or DB writers) from artificially starving the task queue.
3. **Graceful Shutdown:** `atexit` hooks and SIGTERM signal handlers ensure that if the main process is interrupted, the ThreadPool blocks until active tasks complete or securely serialize their current state to disk.

**Phase D: High-Concurrency Persistence**
1. **Micro-Batching:** To resolve the DuckDB concurrent write bottleneck, `db_manager.py` no longer commits every single queue item instantly. The dedicated DB worker thread aggregates writes into **micro-batches** (e.g., every 50ms or 100 items) and executes them in a single transaction.
2. **WAL Optimization:** DuckDB is configured with Write-Ahead Logging (WAL) enabled, maximizing write throughput while maintaining ACID compliance across the 8 execution threads.

### 3. Core Component Upgrades Summary

| Component | Vulnerability/Issue Resolved | Architectural Upgrade |
| :--- | :--- | :--- |
| **`tg_gateway.py`** | Command Injection via Blacklisting | Implemented strict Whitelist execution and sandboxed parameterization. |
| **`mailbox/` IPC** | Git Rate Limits, Merge Conflicts, Race Conditions | Disabled `git_ipc` via `local_config.json`. Replaced with `mesh_api.py`. Added atomic file rename checks for fallback. |
| **`crypto_auth.py`** | Unauthenticated Payloads | Enforces Ed25519 signature verification on all cross-node JSON payloads. |
| **`mas_wrapper.py`** | Silent Data Loss, Thread Starvation | Migrated to `ThreadPoolExecutor` with a dedicated Semaphore and graceful shutdown hooks. |
| **`db_manager.py`** | OLTP Write Bottlenecks | Implemented queue micro-batching and transactional commits for DuckDB. |

### [SYSTEM STATUS]
Architecture finalized. The system is operating under the **High-Performance (Unlocked)** profile. Awaiting operator authorization to branch the repository and commit these architectural upgrades to the `bin/` directory.
