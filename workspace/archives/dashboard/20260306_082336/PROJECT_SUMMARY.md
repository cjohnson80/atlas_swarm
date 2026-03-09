# Project Scratchpad

Goal: Status

## Acceptance Criteria
### Acceptance Criteria: System Status Report

- [ ] **AC 1: Resource Utilization Metrics**
  - The status report must include current CPU and Memory usage percentages (verifiable via `bin/monitor.py` or system utilities).
  - The report must confirm the system is operating within the constraints of the "High-Performance" hardware profile (8 cores, ~11.58 GB RAM).

- [ ] **AC 2: Configuration & Profile State**
  - The report must explicitly list the active hardware profile defined in `core/SOUL.md` and `core/local_config.json`.
  - The report must list currently disabled features (e.g., `db_validator`, `legacy_io_operations`) to ensure alignment with the conservation principle.

- [ ] **AC 3: Active Goals & Heartbeat**
  - The report must extract and display the current active goals/tasks from `core/HEARTBEAT.md`.
  - The report must indicate the timestamp of the last heartbeat or system evolution cycle.

- [ ] **AC 4: Workspace & Project Focus**
  - The system must read and display the currently focused project from `core/current_project.txt`.
  - The system must report the active machine focus (e.g., reading from the `current_focus.json` equivalent or `MY_HOSTNAME`).

- [ ] **AC 5: Service Health Verification**
  - The status output must indicate whether the core engine (`bin/atlas_core.py`) and Telegram Gateway (`bin/tg_gateway.py`) are actively running or ready to receive commands.
  - Any critical errors from recent logs (e.g., `logs/audit.log` or `logs/atlas_core.log`) must be summarized if present.

## Architecture
Here is the **Refined Architecture Plan for the Status Aggregation Subsystem**, engineered to address all security vulnerabilities, scalability bottlenecks, and error-handling deficiencies identified in the critique. 

This blueprint aligns with our High-Performance profile (8 Cores / 11.58 GB RAM) by utilizing safe, bounded concurrency while maintaining strict system governance.

---

### Refined Architecture: Status Aggregation Subsystem (v2.0)

#### 1. Security & Governance Layer
*   **Strict Authorization Enforcement:** The `/status` command in `tg_gateway.py` will be explicitly wrapped with the existing `is_authorized(update)` function. Unverified Telegram IDs will be silently dropped or logged as unauthorized access attempts.
*   **Output Sanitization (Anti-Injection):** A new utility function, `sanitize_for_telegram(text)`, will strip or escape unclosed Markdown/HTML tags from dynamically read files (`HEARTBEAT.md`, logs, project names) before formatting the final Telegram message.
*   **Secure Cache Permissions:** When writing to `data/state/current_status.json`, the subsystem will use `os.open` with `os.O_CREAT | os.O_WRONLY` and explicitly set file permissions to `0o600` (read/write by owner only) via `os.chmod()` to prevent local privilege escalation or spoofing.

#### 2. Scalability & Concurrency Model
*   **Bounded Thread Pool:** Instead of spawning unbounded threads per request, `status_aggregator.py` will utilize `concurrent.futures.ThreadPoolExecutor(max_workers=5)`. This leverages the 8-core architecture for parallel I/O without risking thread exhaustion during command spam.
*   **Strict Cache TTL:** The cache will implement a `STATUS_CACHE_TTL = 15` (seconds). Requests arriving within the TTL will be served directly from memory/disk. Requests outside the TTL will trigger a background regeneration.
*   **Thread-Safe State Management:** A global `threading.Lock()` (e.g., `status_cache_lock`) will wrap all read/write operations to `current_status.json`, eliminating race conditions between the background scheduler and on-demand Telegram requests.

#### 3. Component Breakdown & Error Handling

**I. `MetricsCollector` (AC 1)**
*   **Logic:** Fetches CPU and RAM usage via `psutil`.
*   **Refinement:** Wraps `psutil.cpu_percent` and `psutil.virtual_memory` in `try/except Exception` blocks, returning `{"status": "METRICS_UNAVAILABLE"}` upon failure instead of crashing the thread.

**II. `ConfigValidator` (AC 2)**
*   **Logic:** Parses `core/local_config.json` and `core/SOUL.md`.
*   **Refinement:** Implements graceful degradation. If files are missing, catches `FileNotFoundError` and returns `{"profile": "UNKNOWN", "disabled_features": []}`.

**III. `GoalTracker` (AC 3)**
*   **Logic:** Parses `core/HEARTBEAT.md` for active/completed goals.
*   **Refinement:** Catches `FileNotFoundError` (returns `{"status": "HEARTBEAT_MISSING"}`). Applies `sanitize_for_telegram()` to all extracted goal strings to prevent markdown injection.

**IV. `WorkspaceContext` (AC 4)**
*   **Logic:** Reads `core/current_project.txt` and `~/atlas_agents/core/current_focus.json`.
*   **Refinement:** Utilizes `.get()` safely on JSON loads and catches `FileNotFoundError`, defaulting to `{"project": "default", "focus": "local"}`.

**V. `ServiceHealthMonitor` (AC 5)**
*   **Logic:** Checks process health and tails logs.
*   **Refinement (Process Iteration):** Wraps `psutil.process_iter()` in `try/except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess)` to safely ignore protected or dead processes.
*   **Refinement (Log Tailing):** Completely abandons reading files into memory. Implements `collections.deque(open(logfile, 'r'), maxlen=50)` to efficiently read only the last 50 lines of `audit.log` and `atlas_core.log` with near-zero memory overhead.

#### 4. Execution Flow
1.  **Request:** Operator sends `/status`.
2.  **Auth Check:** `tg_gateway.py` verifies operator ID.
3.  **Cache Check:** Aggregator acquires `status_cache_lock`. Checks if `current_status.json` is `< 15s` old.
    *   *If valid:* Returns cached JSON immediately.
    *   *If stale/missing:* Proceeds to generation.
4.  **Parallel Execution:** Dispatches the 5 components to the `ThreadPoolExecutor`.
5.  **Aggregation & Sanitization:** Awaits futures, handles any component-level timeouts, and sanitizes all string outputs.
6.  **Secure Write:** Writes the new state to `current_status.json` with `0o600` permissions. Releases lock.
7.  **Delivery:** Formats the sanitized JSON into a clean Telegram MarkdownV2 message and transmits.

---

### Next Steps for Implementation
With this hardened architecture, I am ready to generate the required source code for `bin/status_aggregator.py` and patch `bin/tg_gateway.py`. 

Shall I proceed with creating the implementation branch and writing the code?
