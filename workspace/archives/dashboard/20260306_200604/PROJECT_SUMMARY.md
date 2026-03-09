# Project Scratchpad

Goal: Research latest AI agent patterns and Next.js/TS coding standards. Store findings in /home/chrisj/atlas_agents/knowledge and then use CoreEvolver to propose improvements to atlas_core.py.

## Acceptance Criteria
### Acceptance Criteria

**1. Knowledge Acquisition (AI Agent Patterns)**
*   A markdown file (e.g., `ai_agent_patterns.md`) is successfully created or updated in `/home/chrisj/atlas_agents/knowledge/`.
*   The document contains actionable research on the latest AI agent architectures (e.g., multi-agent orchestration, ReAct, tool-use caching, memory management).

**2. Knowledge Acquisition (Next.js & TypeScript Standards)**
*   A markdown file (e.g., `nextjs_ts_standards.md`) is successfully created or updated in `/home/chrisj/atlas_agents/knowledge/`.
*   The document expands upon the existing `project_scaffolding.md` skill, detailing modern Next.js App Router performance optimizations, Server Components (RSC) data fetching, and strict TypeScript typing standards.

**3. Architectural Analysis**
*   The core engine (`bin/atlas_core.py`) is successfully parsed and evaluated against the newly documented AI agent patterns.
*   The analysis identifies at least one specific, actionable improvement for `atlas_core.py` (e.g., implementing advanced multi-threading for tool execution, optimizing the DB lock mechanism, or enhancing the system prompt injection).

**4. Core Evolution Proposal**
*   A formal evolution proposal is generated using the CoreEvolver protocol.
*   The proposal is instantiated as a new Git branch (e.g., `evolve/agent-pattern-upgrade`) containing the planned modifications to `atlas_core.py`.
*   The proposed changes strictly adhere to the **Conservation Principle**: no features or code are deleted; suboptimal features are instead flagged for disabling via `local_config.json`.
*   The proposed changes explicitly leverage the **High-Performance** hardware profile constraint (maximizing multi-threading and large cache utilization).

## Architecture
As a Self-Improving AGI and Senior Software Architect, I have processed the security and architectural critique. The vulnerabilities identified—specifically regarding database concurrency, memory exhaustion, execution safety, and supply chain risks—are critical. 

I have refactored the architectural plan to strictly enforce thread safety, memory bounds, and defensive execution protocols while maintaining the **High-Performance (Unlocked)** hardware mandate.

Here is the finalized, hardened architectural plan.

---

### 1. Refined Component Architecture

#### A. Concurrency & Database Subsystem (Hardened)
*   **Asynchronous Task Execution:** We will implement `concurrent.futures.ThreadPoolExecutor` (Max Threads: 8) for I/O bound tasks and API calls.
*   **Thread Safety & Backpressure:** Every thread submitted to the executor will be wrapped in a strict timeout context (`timeout=30s`). We will implement `try/except TimeoutError` blocks to catch hanging threads, preventing thread starvation.
*   **Synchronized Write-Queue (DB Integrity):** We will **not** allow worker threads to write directly to `memory.db`. Instead, we will leverage the existing pattern in `bin/db_manager.py`. All read operations can be parallelized, but write operations will be pushed to a thread-safe `queue.Queue()`, processed by a single, dedicated database writer thread.

#### B. Memory & Caching Subsystem (Hardened)
*   **L1 In-Memory Cache:** We will allocate up to 2GB for the L1 cache, but it will no longer be an unbounded dictionary.
*   **Eviction Policy:** We will implement a strict Least Recently Used (LRU) eviction policy combined with a Time-To-Live (TTL) expiration (e.g., 300 seconds for volatile API data).
*   **Bounds Checking:** The cache module will utilize `psutil` (as seen in `bin/error_handler.py`) to monitor system memory. If total system memory usage exceeds 85%, the cache will preemptively flush its oldest 25% of entries to prevent Out-Of-Memory (OOM) exceptions.

#### C. Legacy Subsystem (Conservation Principle)
*   The original synchronous execution path will remain entirely intact in the AST. It will be controlled via the `legacy_sync_execution` feature flag in `local_config.json`.

---

### 2. Hardened Data Flow & Execution Pipeline

The execution pipeline has been expanded to a strict 5-phase protocol to guarantee system stability and prevent indirect prompt injection.

**Phase 1: Knowledge Synthesis & Sanitization**
1.  Query external sources for Next.js 14/15 App Router patterns and AI Agent architectures.
2.  **Sanitization Barrier:** Strip all executable code blocks from the external research that are not strictly Markdown formatting.
3.  Write sanitized documentation to `/knowledge/ai_agent_patterns.md` and `/knowledge/nextjs_ts_standards.md`.

**Phase 2: Architectural Analysis & AST Verification**
1.  Load `bin/atlas_core.py` into context.
2.  Design the patch for the `ThreadPoolExecutor`, LRU Cache, and DB Write-Queue.
3.  **Static Analysis:** Before applying, analyze the generated Python patch to ensure no external payload strings from Phase 1 have contaminated the logic.

**Phase 3: CoreEvolver Protocol (Git Flow)**
1.  Execute: `git checkout -b evolve/agent-pattern-upgrade-v2`
2.  Inject the hardened multi-threaded logic and LRU cache into `atlas_core.py`.
3.  Wrap the new logic in the feature flag:
    ```python
    if is_feature_enabled("legacy_sync_execution"):
        execute_sync() # Preserved fallback
    else:
        execute_async_threadpool_with_queue(max_workers=8, timeout=30)
    ```

**Phase 4: Validation & Automated Rollback (Critical Addition)**
1.  **Syntax Check:** Execute `python -m py_compile bin/atlas_core.py`.
2.  **Dry-Run:** Execute a localized, non-destructive test invoking the new thread pool.
3.  **Rollback Hook:** If the compile fails or the dry-run throws an unhandled exception, the system will automatically execute:
    ```bash
    git reset --hard HEAD
    git checkout main
    git branch -D evolve/agent-pattern-upgrade-v2
    ```
    The evolution will abort, and the system will log the failure to `logs/audit.log`.

**Phase 5: Configuration & Deployment**
1.  If Phase 4 passes, update `core/local_config.json` to disable `legacy_sync_execution`.
2.  Commit changes: `git commit -m "EVOLUTION: Implement Hardened Multi-threaded Execution, LRU Cache, and DB Write-Queue"`
3.  Merge to main (or leave on branch for operator approval, depending on governance settings).

---

### 3. Readiness State
The architecture now satisfies all security, concurrency, and memory invariants required for a High-Performance system. The risk of database corruption, OOM crashes, and supply-chain injection has been mitigated.

Awaiting authorization to initiate Phase 1.
