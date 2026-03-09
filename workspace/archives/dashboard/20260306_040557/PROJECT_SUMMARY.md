# Project Scratchpad

Goal: Research latest AI agent patterns and Next.js/TS coding standards. Store findings in /home/chrisj/atlas_agents/knowledge and then use CoreEvolver to propose improvements to atlas_core.py.

## Acceptance Criteria
### Acceptance Criteria

- [ ] **Knowledge Base Population (AI Patterns):** A markdown file (e.g., `ai_agent_patterns.md`) is successfully created and populated in `/home/chrisj/atlas_agents/knowledge/` containing actionable research on modern AI agent patterns (e.g., multi-agent orchestration, memory management, tool-use strategies).
- [ ] **Knowledge Base Population (Next.js/TS):** A markdown file (e.g., `nextjs_ts_standards.md`) is successfully created or updated in `/home/chrisj/atlas_agents/knowledge/` detailing current Next.js (App Router) and strict TypeScript coding standards.
- [ ] **CoreEvolver Execution:** The CoreEvolver process is successfully triggered and completes an analysis of `bin/atlas_core.py` using the newly gathered research.
- [ ] **Improvement Proposal Generation:** A concrete improvement proposal (e.g., a git branch, a diff, or a structured markdown document) is generated for `atlas_core.py` that directly applies at least one newly researched AI pattern.
- [ ] **Constraint Adherence:** The proposed modifications to `atlas_core.py` strictly obey the Conservation Principle (no features are deleted, only disabled via `local_config.json`) and align with the High-Performance hardware profile (maintaining or enhancing multi-threading/cache usage).

## Architecture
Here is the refined CoreEvolver architecture plan. It strictly integrates the necessary security, scalability, and error-handling safeguards identified in the critique while maintaining maximum alignment with the High-Performance (8-core, 2GB cache) hardware profile and the Conservation Principle.

### 1. Target Directory Structure (Revised)
The directory structure has been expanded to include a secure sandbox for validation and explicit rollback mechanisms.

```text
~/atlas_agents/
├── knowledge/                             
│   ├── ai_agent_patterns.md               # Multi-agent orchestration, bounded memory, tool-use
│   └── nextjs_ts_standards.md             # App Router, RSCs, Strict TS
├── core/
│   ├── local_config.json                  # ENFORCEMENT: Feature toggles (Conservation Principle)
│   └── SOUL.md                            
├── bin/
│   ├── atlas_core.py                      # TARGET: Core engine
│   ├── approval_manager.py                # INTEGRATION: Governance and operator consent
│   └── tools/
│       └── core_evolver.py                # PROPOSED: Safe AST parser, validator, and diff generator
├── scripts/
│   └── auto_rollback.sh                   # NEW: Automated Git revert trigger for failed health checks
└── workspace/
    ├── proposals/                         # Output directory for diffs
    └── sandbox/                           # NEW: Isolated environment for AST validation and dry-runs
```

### 2. Data Flow Architecture (Revised for Safety & Scalability)
The execution pipeline now enforces strict validation, governance gating, and bounded execution.

1.  **Phase 1: Knowledge Synthesis (I/O Bound)**
    *   *Action:* Aggregate data on ReAct patterns, Semantic Routing, Next.js 15, and strict TypeScript.
    *   *Output:* Write structured markdown to the `knowledge/` directory.
2.  **Phase 2: CoreEvolver Static Analysis & Generation (CPU Bound)**
    *   *Action:* Ingest `bin/atlas_core.py` as an Abstract Syntax Tree (AST).
    *   *Drafting:* Generate the "Multi-Threaded Semantic Tool Router" implementation.
    *   *Constraint Check:* Ensure legacy logic is preserved and gated behind `if not is_feature_enabled('legacy_sequential_tools'):`.
3.  **Phase 3: Validation & Governance Gating (Security Bound)**
    *   *Syntax Validation:* Run `ast.parse()` on the proposed `atlas_core.py` code in memory.
    *   *Dry-Run:* Execute a simulated initialization in `workspace/sandbox/` to verify module imports and absence of immediate fatal errors.
    *   *Governance:* Call `ApprovalManager.submit_request()` with a high risk score (e.g., 90.0) detailing the AST modification. **Execution halts until the Telegram Gateway receives an `APPROVE` command.**
4.  **Phase 4: Bounded Execution & Rollback Protocol (Compute Bound)**
    *   *Action:* Upon approval, apply the diff via a new Git branch (`feature/evo-agentic-patterns`).
    *   *Health Check:* Restart the local agent process. If the process crashes or fails to emit a heartbeat within 10 seconds, `scripts/auto_rollback.sh` is triggered to `git revert` the merge and restore the previous state.

### 3. Component Breakdown & Refinements

#### A. Target: `atlas_core.py` (The Multi-Threaded Semantic Tool Router)
The proposed evolution will replace the sequential tool loop with a highly concurrent, yet strictly bounded, execution model optimized for the 8-core CPU.

*   **Bounded Thread Pool:** Instead of spawning unbounded threads, the router will utilize `concurrent.futures.ThreadPoolExecutor(max_workers=8)` (dynamically read from `probe_system_defaults()`).
*   **Concurrency Locks:** Read-only tools (e.g., web scraping, API fetches) will execute in parallel. State-mutating tools (e.g., file writes, `duckdb` inserts) will be forced to acquire the existing `db_lock` or a new `file_io_lock` to prevent race conditions.
*   **Strict Timeouts:** Every tool execution submitted to the thread pool will be wrapped with a strict timeout (`future.result(timeout=15)`). If a tool hangs, the thread is released, the error is caught, and a partial-success payload is returned to the LLM.
*   **Payload Sanitization:** All LLM-generated tool arguments will pass through a strict type-checking and sanitization layer before execution to prevent command injection.

#### B. Cache & Memory Management (Addressing OOM Vulnerability)
To safely utilize the 2GB cache profile without poisoning or memory fragmentation:
*   **Size Limits:** Tool output payloads will be truncated if they exceed a dynamically calculated threshold (e.g., 50MB per tool).
*   **TTL & Eviction:** The `bin/cache_utils.py` will be updated to enforce strict Time-To-Live (TTL) policies and an LRU (Least Recently Used) eviction strategy if the cache directory exceeds 80% of the allocated 2GB.

#### C. CoreEvolver Engine (`bin/tools/core_evolver.py`)
*   **Role:** Safely generate, validate, and apply self-improvements.
*   **Safety Mechanism:** It will never write directly to `bin/atlas_core.py` without first passing the `ast.parse()` check and receiving an explicit `True` boolean from the `ApprovalManager`.

### 4. Summary of Safeguards Implemented

| Vulnerability / Risk | Mitigation Strategy Implemented |
| :--- | :--- |
| **Bypass of Governance** | Hard dependency on `bin/approval_manager.py` before any Git diff application. |
| **Unsafe Concurrency** | Implementation of `db_lock` and `file_io_lock` for state-mutating tools. |
| **Command Injection** | Strict schema validation and sanitization of all LLM tool payloads prior to execution. |
| **Pre-Merge Validation** | Mandatory `ast.parse()` syntax checking and sandbox dry-runs. |
| **Thread Exhaustion** | Bounded execution using `ThreadPoolExecutor(max_workers=8)`. |
| **Cache Poisoning / OOM** | Strict per-payload size limits (50MB) and LRU eviction within the 2GB cache limit. |
| **Hanging Threads** | Enforced execution timeouts (`future.result(timeout=15)`) with partial-success aggregation. |
| **System Bricking** | Automated `scripts/auto_rollback.sh` triggered by post-merge heartbeat failure. |

If this refined architecture successfully resolves all security, scalability, and error-handling concerns, I am ready to initialize **Phase 1: Knowledge Synthesis**. Please authorize the execution.
