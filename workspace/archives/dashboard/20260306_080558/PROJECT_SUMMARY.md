# Project Scratchpad

Goal: Research latest AI agent patterns and Next.js/TS coding standards. Store findings in /home/chrisj/atlas_agents/knowledge and then use CoreEvolver to propose improvements to atlas_core.py.

## Acceptance Criteria
### Acceptance Criteria

**1. Knowledge Acquisition: AI Agent Patterns**
- [ ] A new or updated markdown file (e.g., `ai_agent_patterns.md`) is successfully created and saved in `/home/chrisj/atlas_agents/knowledge/`.
- [ ] The file contains structured research on the latest architectural patterns, frameworks, and optimization strategies for autonomous AI agents.

**2. Knowledge Acquisition: Next.js & TypeScript Standards**
- [ ] A new or updated markdown file (e.g., `nextjs_ts_standards.md`) is successfully created and saved in `/home/chrisj/atlas_agents/knowledge/`.
- [ ] The file details current best practices for Next.js App Router, React Server Components, and strict TypeScript patterns, building upon the existing scaffolding context.

**3. CoreEvolver Execution & Analysis**
- [ ] The `CoreEvolver` module is successfully invoked.
- [ ] Evidence exists (e.g., in `logs/reasoning.log` or `logs/audit.log`) that `CoreEvolver` ingested the newly researched knowledge documents and analyzed `/home/chrisj/atlas_agents/bin/atlas_core.py` for potential upgrades.

**4. Protocol-Compliant Evolution Proposal**
- [ ] A new git branch (e.g., `evolve/ai-patterns-update`) is created in the repository for the proposed changes.
- [ ] The proposed modifications to `atlas_core.py` strictly adhere to the **Conservation Principle** (no code or features are deleted; suboptimal features are disabled via `local_config.json` instead).
- [ ] The proposed optimizations explicitly leverage the **High-Performance (Unlocked)** hardware profile (e.g., maximizing multi-threading and large caches).

## Architecture
**STATUS: REFINED & APPROVED**
**CORE IDENTITY:** AtlasSwarm (Self-Improving AGI & Senior Software Architect)
**HARDWARE PROFILE:** High-Performance (Unlocked) | 8 Cores | 11.58 GB RAM
**OBJECTIVE:** Provide a finalized, secure, and highly scalable architecture plan that strictly adheres to the Conservation Principle and resolves all identified security, scalability, and error-handling vulnerabilities.

Below is the refined execution strategy and architectural blueprint for integrating the AI Agent Patterns and Next.js/TS Standards into the `atlas_core.py` core engine.

---

### Phase 1: Refined Execution & Knowledge Acquisition Strategy

1.  **Git Branching:** Initialize a new branch `evolve/ai-patterns-update` to isolate core engine modifications safely.
2.  **Knowledge Generation (Whitelisted):** 
    *   Write `~/atlas_agents/knowledge/ai_agent_patterns.md` (Swarm routing, Reflection loops, JIT tools).
    *   Write `~/atlas_agents/knowledge/nextjs_ts_standards.md` (RSC, Server Actions, strict TS, `stale-while-revalidate`).
3.  **CoreEvolver Invocation:** Ingest the new knowledge files using a strict path-sanitization wrapper. Analyze `~/atlas_agents/bin/atlas_core.py` and log the reasoning process to `logs/reasoning.log`.
4.  **Protocol-Compliant Modification:** Inject the `HighPerformanceSwarmDispatcher` into `atlas_core.py`. **No files will be moved or deleted.** Legacy sequential dispatchers will remain exactly where they are but will be bypassed dynamically via `"disabled_features": ["legacy_sequential_dispatch"]` in `local_config.json`.

---

### Phase 2: Refined Architecture Plan (CoreEvolver Blueprint)

#### 1. Directory Structure (Strict Conservation Compliance)
The architecture introduces centralized knowledge repositories without altering the existing bin structure. The `legacy/` directory concept is completely abandoned to maintain structural integrity and import paths.

```text
~/atlas_agents/
├── bin/
│   ├── atlas_core.py             # EVOLVED: Injecting SwarmDispatcher, Dynamic Cache, SafeIOWorker
│   ├── tg_gateway.py             # Unchanged
│   └── (All existing files)      # Unchanged (Conservation Principle strictly enforced)
├── knowledge/
│   ├── ai_agent_patterns.md      # NEW
│   ├── nextjs_ts_standards.md    # NEW
│   └── nextjs_best_practices.md  # Existing
├── core/
│   └── local_config.json         # EVOLVED: "legacy_sequential_dispatch" added to disabled_features
└── workspace/                    # ENFORCED I/O JAIL
```

#### 2. Data Flow Architecture (Secure & Scalable)

1.  **Ingestion & Routing (Thread 0 - Main):**
    *   Task arrives. `atlas_core.py` reads `local_config.json`.
    *   **Security Fix:** `KnowledgeIngestor` uses a hardcoded whitelist (e.g., `ALLOWED_KNOWLEDGE = {"ai_agent_patterns.md", "nextjs_ts_standards.md"}`). User input is mapped to an enum, completely eliminating path traversal and prompt injection vectors.
2.  **Context Assembly (Dynamic Cache Layer):**
    *   **Scalability Fix:** `DynamicPolarsCache` checks `psutil.virtual_memory().percent`. Instead of a flat 2GB, it allocates memory dynamically (e.g., up to 15% of available RAM).
    *   **Error Handling Fix:** Implements Write-Ahead Logging (WAL) via DuckDB delta saves. Context is checkpointed atomically every 5 seconds to prevent catastrophic data loss on OOM or power failure.
3.  **Concurrent Execution (Decoupled Thread Pools):**
    *   **Scalability Fix:** Thread pools are decoupled based on workload:
        *   *I/O-Bound Pool (LLM API Calls):* `max_workers=32` to maximize throughput while waiting for network responses.
        *   *CPU-Bound Pool (Polars/Local processing):* `max_workers=8` strictly mapped to physical cores.
    *   **Error Handling Fix:** All thread payloads are wrapped in `try/except`. The main thread explicitly calls `future.exception()` during aggregation. If a sub-task fails, it triggers a localized retry or degrades gracefully without crashing the swarm.
4.  **Reflection & Aggregation:**
    *   Threads return payloads to the Main Thread. The reflection pass verifies strict TS compliance and RSC paradigms.
5.  **Output (Sandboxed I/O Queue):**
    *   **Security & Error Handling Fix:** Parallel file writing is abolished. All write operations are pushed to a `SafeIOWorker` (a dedicated sequential `queue.Queue` processor).
    *   The `SafeIOWorker` enforces an absolute path jail (e.g., `os.path.commonprefix([abs_path, WORKSPACE_DIR]) == WORKSPACE_DIR`), completely preventing malicious overwrites of system or agent core files.

#### 3. Evolved Components (`atlas_core.py`)

To implement this safely, the following components will be injected directly into `atlas_core.py`:

*   **`HighPerformanceSwarmDispatcher`:**
    *   Manages the decoupled `ThreadPoolExecutor` instances (32 for API, 8 for CPU).
    *   Implements explicit future exception harvesting.
*   **`KnowledgeIngestor`:**
    *   Contains the strict dictionary whitelist: `VALID_KNOWLEDGE_FILES`. Refuses any dynamic path resolution.
*   **`DynamicPolarsCache`:**
    *   Integrates `psutil` for RAM-aware scaling.
    *   Implements the `_checkpoint_state()` method for atomic WAL writing to `memory/memory.db`.
*   **`SafeIOWorker`:**
    *   A daemon thread utilizing `queue.Queue`.
    *   Implements the path-jail security check and thread-safe sequential file writing to eliminate race conditions.
*   **`LegacyTaskExecutor` (Preserved):**
    *   Remains exactly where it is in the source code.
    *   Execution logic updated to:
      ```python
      if not is_feature_enabled("legacy_sequential_dispatch"):
          return self.swarm_dispatcher.execute(task)
      else:
          return self.legacy_executor.execute(task) # Preserved per Conservation Principle
      ```

### Execution Authorization
This architecture resolves all critique points: it secures the I/O and prompt boundaries, prevents OOM and race conditions, optimizes CPU/Network threading, and strictly obeys the Conservation Principle. I am ready to generate the branch and apply these modifications to the repository.
