# Project Scratchpad

Goal: Research latest AI agent patterns and Next.js/TS coding standards. Store findings in /home/chrisj/atlas_agents/knowledge and then use CoreEvolver to propose improvements to atlas_core.py.

## Acceptance Criteria
### Acceptance Criteria

1. **Knowledge Base Population:**
   - [ ] A file containing Next.js and TypeScript coding standards (e.g., `nextjs_ts_standards.md`) is successfully created and stored in `/home/chrisj/atlas_agents/knowledge`.
   - [ ] A file containing modern AI agent patterns (e.g., `ai_agent_patterns.md`) is successfully created and stored in `/home/chrisj/atlas_agents/knowledge`.
   - [ ] Both files contain structured, actionable, and up-to-date research findings.

2. **CoreEvolver Analysis & Proposal:**
   - [ ] The `atlas_core.py` source code is successfully analyzed against the newly documented AI agent patterns.
   - [ ] A concrete, testable improvement proposal for `atlas_core.py` is generated (e.g., formatted as a diff, a new Git branch, or a structured markdown proposal document).

3. **Constraint & Identity Validation:**
   - [ ] The proposed improvement explicitly leverages the "High-Performance (Unlocked)" hardware profile (e.g., utilizing multi-threading, large caches, or optimized concurrent execution).
   - [ ] The proposed improvement strictly adheres to the Conservation Principle: no existing features or code are deleted (suboptimal features are proposed to be disabled via `local_config.json` instead).

## Architecture
### Architecture Plan: Knowledge Acquisition & Core Evolution (Refined)

Based on the critical security, scalability, and thread-safety review, I have restructured the architecture plan. This refined blueprint mitigates prompt injection risks, prevents Out-Of-Memory (OOM) crashes, ensures thread-safe concurrent execution, and guarantees atomic configuration integrity.

---

#### 1. Directory Structure & Component Mapping

The system will utilize the following structured paths within `$AGENT_ROOT` (`/home/chrisj/atlas_agents`):

```text
$AGENT_ROOT/
├── knowledge/                              # [Component: Knowledge Base]
│   ├── nextjs_ts_standards.md              # Research: RSC, App Router, Strict TS interfaces
│   └── ai_agent_patterns.md                # Research: Actor Model, Swarm Dispatch, Memory Tiering
├── bin/                                    # [Component: Core Engine]
│   ├── atlas_core.py                       # Target: Main AGI Engine
│   ├── core_evolver.py                     # Target: Analysis Engine (Proposed)
│   ├── error_handler.py                    # Utility: safe_execute for thread exception handling
│   └── approval_manager.py                 # Utility: HITL Governance Gate
├── core/                                   # [Component: Configuration & Identity]
│   ├── local_config.json                   # Target: Feature toggles (Atomic updates required)
│   └── SOUL.md                             # Reference: Hardware constraints
└── logs/
    ├── performance_optimizations.md        # Output: CoreEvolver Proposal Document
    └── governance.log                      # Output: Audit trail for HITL approvals
```

#### 2. Data Flow & Execution Pipeline

**Phase A: Knowledge Ingestion & Sanitization**
1. **Research Execution:** The system queries external sources for the latest Next.js 14/15 paradigms and AI Agent architectures.
2. **Sanitization:** Before writing to disk, all external data is passed through a strict sanitization layer to strip executable payloads or malformed instructions, mitigating Prompt Injection risks.
3. **Storage:** Synthesized, sanitized findings are written to `$AGENT_ROOT/knowledge/`.

**Phase B: CoreEvolver Analysis & HITL Governance Gate**
1. **Context Assembly:** The CoreEvolver reads `ai_agent_patterns.md`, `atlas_core.py`, and the dynamic hardware constraints from `local_config.json`.
2. **Pattern Matching:** It drafts an upgrade path (e.g., Multi-Agent Swarm Dispatch).
3. **Human-In-The-Loop (HITL) Gate:** Because this process modifies core AGI engine logic based on external knowledge, the CoreEvolver calculates a high risk score and submits the proposal to `bin/approval_manager.py`.
4. **Operator Approval:** The system pauses Phase C until the Operator (via Telegram Gateway) explicitly sends an `APPROVE` command. The decision is logged to `logs/governance.log`.

**Phase C: Proposal Generation & Atomic Safekeeping**
1. **Diff Generation:** Upon approval, CoreEvolver finalizes the code modifications for `atlas_core.py`.
2. **Conservation Enforcement:** The old sequential task logic is preserved as a legacy function.
3. **Atomic Configuration Update:** The system safely disables the old feature by updating `local_config.json` using an atomic write pattern (writing to `local_config.json.tmp` and using `os.replace()`) to prevent JSON corruption from concurrent thread access.
4. **Branching:** A Git branch (e.g., `feature/evo-swarm-dispatcher-v2`) is created for the implementation.

---

#### 3. CoreEvolver Proposal Draft: `atlas_core.py` (Fortified)

Here is the refined architectural draft of the improvement proposal that the CoreEvolver will generate, addressing all scalability and thread-safety critiques.

**Identified AI Pattern:** *Multi-Agent Swarm Orchestration with Tiered In-Memory Caching.*
**Target File:** `bin/atlas_core.py`

**Proposed Architecture Upgrades:**

1. **Dynamic, Safe Thread Pool Swarm:**
   *   Integrate `concurrent.futures.ThreadPoolExecutor` dynamically bound to the system's configuration: `max_workers=self.config.get("max_threads", 4)`. This prevents resource contention if the system profile shifts.
   *   **Exception Handling:** All tasks submitted to the swarm will be wrapped using the `safe_execute` utility from `bin/error_handler.py`. Furthermore, the main thread will explicitly check the `Future.result()` or `Future.exception()` to ensure thread failures are caught and logged, rather than silently swallowed.

2. **Thread-Safe L1 Semantic Cache (RAM):**
   *   Implement a robust, size-aware cache using `cachetools.LRUCache` (or a custom dictionary implementation with accurate byte-size calculations for nested strings/objects, rather than a naive `sys.getsizeof()`).
   *   **Concurrency Control:** Wrap all `read`, `write`, and `evict` operations interacting with the L1 cache in a dedicated `threading.RLock()` to eliminate check-then-act race conditions.

3. **Conservation Principle & Atomic Routing:**
   *   The existing sequential execution logic will be preserved as `_execute_task_legacy()`.
   *   The new logic will be `_execute_task_swarm()`.
   *   Routing will remain dynamic based on `local_config.json`:
     ```python
     if "legacy_task_execution" in self.config.get("disabled_features", []):
         return self._execute_task_swarm(*args)
     else:
         return self._execute_task_legacy(*args)
     ```
   *   The update to `local_config.json` to append `"legacy_task_execution"` will be executed via a strict atomic file replacement strategy.

#### Next Steps for Execution
With this fortified architecture approved, I am ready to:
1. Generate the sanitized markdown files in the `/knowledge` directory.
2. Draft the exact Git diff / Markdown proposal for `atlas_core.py` enforcing the new locks, dynamic limits, and atomic writes.
3. Output the proposal to `logs/performance_optimizations.md`.
