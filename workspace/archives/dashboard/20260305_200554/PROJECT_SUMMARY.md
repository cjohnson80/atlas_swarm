# Project Scratchpad

Goal: Research latest AI agent patterns and Next.js/TS coding standards. Store findings in /home/chrisj/atlas_agents/knowledge and then use CoreEvolver to propose improvements to atlas_core.py.

## Acceptance Criteria
### Acceptance Criteria

**1. AI Agent Patterns Research Documented**
- **Condition:** A markdown file (e.g., `ai_agent_patterns.md` or updated `ai_trends.md`) must exist in `/home/chrisj/atlas_agents/knowledge`.
- **Validation:** The file contains detailed, actionable research on modern AI agent architectures (e.g., ReAct, Plan-and-Solve, memory management, multi-agent orchestration, and tool-use optimization).

**2. Next.js & TypeScript Standards Documented**
- **Condition:** A markdown file (e.g., `nextjs_ts_standards.md` or updated `nextjs_best_practices.md`) must exist in `/home/chrisj/atlas_agents/knowledge`.
- **Validation:** The document outlines current best practices, explicitly covering App Router, React Server Components (RSC), Server Actions, and strict TypeScript configurations, building upon the existing `project_scaffolding.md` context.

**3. Core Codebase Analysis**
- **Condition:** The system must evaluate `bin/atlas_core.py` against the newly gathered AI agent patterns.
- **Validation:** A formal proposal or internal log entry is generated detailing specific, implementable improvements to `atlas_core.py` (e.g., enhanced prompt injection, more efficient tool orchestration, or better memory handling).

**4. Evolution Implementation via Git Branch**
- **Condition:** The CoreEvolver process must generate and commit the proposed code changes to `atlas_core.py`.
- **Validation:** A new git branch (e.g., `evolve/gemini-mas-architecture`) is created. The branch contains commits that successfully integrate the proposed improvements into the core engine without breaking existing functionality.

**5. Adherence to Core Conservation & Performance Constraints**
- **Condition:** The modifications must respect the anchored core identity rules.
- **Validation:** 
  - **Conservation Principle:** No existing code or features are deleted from `atlas_core.py`. Any deprecated or suboptimal logic is instead disabled via `local_config.json`.
  - **Hardware Profile:** The changes must maintain or enhance the "High-Performance (Unlocked)" constraint, utilizing multi-threading or large cache optimizations where applicable.

## Architecture
As a Senior Software Architect and Self-Improving AGI, I have integrated the critical security, scalability, and error-handling feedback into the system design. To ensure a robust, fail-safe evolution of the `atlas_core.py` core engine, the architecture has been fundamentally restructured. 

We are introducing strict sanitization boundaries, bounded concurrency, explicit governance gates via the Telegram Gateway, and a Watchdog-driven automated rollback mechanism.

Below is the finalized, hardened architecture plan for the self-improvement cycle.

---

### 1. Enhanced Directory Structure & State Management

We will utilize the existing `$AGENT_ROOT` repository, adding specific components for sandboxing, validation, and rollback monitoring.

```text
$AGENT_ROOT/
├── knowledge/                        # 🎯 TARGET: Research Ingestion (Sanitized)
├── core/
│   ├── local_config.json             # 🎯 TARGET: Feature toggling & Thread Limits (max_threads: 8)
│   └── HEARTBEAT.md                  # 🎯 TARGET: Watchdog monitoring target
├── bin/
│   ├── atlas_core.py                 # 🎯 TARGET: Core engine mutation
│   ├── approval_manager.py           # 🛡️ GATE: Operator Approval via Telegram
│   └── watchdog_rollback.sh          # 🛡️ NEW: Automated rollback script
└── tests/
    └── sandbox_eval/                 # 🛡️ NEW: Dry-run execution environment
```

### 2. Hardened Component Architecture

The execution pipeline is now divided into six highly regulated components, ensuring no mutated code reaches production without explicit approval and automated safety nets.

#### A. Secure Knowledge Acquisition Swarm (Research & Sanitization)
*   **Function:** Aggregates AI Agent patterns and Next.js/TS best practices.
*   **Security Upgrade (Data Poisoning):** Implements a strict sanitization boundary. Ingested external text is treated as untrusted data. It is passed through a regex-based stripper to remove executable payloads before being written to `knowledge/*.md`. The Core Evolver will *never* directly execute or `eval()` content from these files; they are strictly used as context for the LLM's AST generation.

#### B. Core Analyzer (Self-Reflection Engine)
*   **Function:** Parses the AST of `bin/atlas_core.py` to identify synchronous bottlenecks and propose the `ParallelReActExecutor`.

#### C. Governance & Approval Gate (The Telegram Barrier)
*   **Function:** Intercepts the proposed AST mutation before any git branching or file writing occurs.
*   **Security Upgrade (Governance):** Interfaces with `bin/approval_manager.py`. The proposed architecture change is assigned a High Risk Score (>50.0). The system halts and forwards the diff to the Operator via the Telegram Gateway. Execution only proceeds upon receiving an explicit `APPROVE` payload.

#### D. Core Evolver (Bounded Code Mutation Engine)
*   **Function:** Executes the git branching (`evolve/gemini-mas-architecture`) and code modification.
*   **Scalability & Security Upgrades:**
    *   *Resource Exhaustion:* The new `ParallelReActExecutor` will use `concurrent.futures.ThreadPoolExecutor` strictly bounded by the `max_threads` value dynamically read from `core/local_config.json` (currently 8 on this High-Performance profile). Unbounded DAG spawning is explicitly prohibited.
    *   *Race Conditions:* The AST mutation will inject explicit `with db_lock:` context managers around all database write operations and utilize `asyncio.Semaphore` for I/O operations to prevent data corruption during parallel tool execution.
    *   *Conservation Principle:* The legacy `SequentialReActExecutor` remains intact. `local_config.json` is updated to `"disabled_features": ["legacy_sequential_executor"]`.

#### E. Sandboxed Validator (Pre-Commit Testing)
*   **Function:** Prevents fatal runtime errors from being committed.
*   **Error Handling Upgrade:** Before committing, the mutated `atlas_core.py` is executed within a restricted `tests/sandbox_eval/` environment. It runs a suite of mock tasks to verify syntax validity, thread safety (no deadlocks), and correct output formatting.

#### F. Watchdog Deployment & Automated Rollback
*   **Function:** Safeguards against "bricking" the agent during the live transition.
*   **Error Handling Upgrade:** A new detached process (`bin/watchdog_rollback.sh`) is spawned before the main engine restarts on the new branch. The watchdog monitors `core/HEARTBEAT.md`. If the new `atlas_core.py` fails to write a valid heartbeat within 60 seconds of startup, the watchdog automatically executes `git checkout main`, restores the previous `local_config.json` state, and restarts the system.

### 3. Strict Data Flow & Execution Pipeline

1.  **Phase 1: Secure Ingestion & Sanitization**
    *   Fetch external data → Sanitize (Strip executable code) → Write to `knowledge/`.
2.  **Phase 2: Analysis & Proposal Generation**
    *   Analyze `atlas_core.py` AST + `knowledge/` context → Generate Mutation Proposal (Bounded DAG Executor).
3.  **Phase 3: Governance Approval**
    *   Submit Proposal to `bin/approval_manager.py` → Wait for Telegram Operator `APPROVE` → Proceed.
4.  **Phase 4: Isolation & Bounded Mutation**
    *   `git checkout -b evolve/gemini-mas-architecture`.
    *   Inject `ParallelReActExecutor` (Bounded by `max_threads: 8`, enforcing `db_lock`).
    *   Update `local_config.json` (Conservation Principle).
5.  **Phase 5: Sandboxed Validation & Dry-Run**
    *   Run unit tests in `tests/sandbox_eval/`. If failure occurs, abort and alert Operator.
6.  **Phase 6: Watchdog-Monitored Deployment**
    *   Spawn `watchdog_rollback.sh` (60s timeout on `HEARTBEAT.md`).
    *   Commit changes → Restart Core Engine → Await successful Heartbeat.

---

**System Readiness:**
This refined architecture strictly adheres to the High-Performance constraints while completely mitigating the risks of data poisoning, race conditions, resource exhaustion, and fatal system failure. 

Awaiting your authorization to initialize Phase 1 and engage the secure research swarm.
