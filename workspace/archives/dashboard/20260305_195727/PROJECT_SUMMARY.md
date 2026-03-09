# Project Scratchpad

Goal: Research latest AI agent patterns and Next.js/TS coding standards. Store findings in /home/chrisj/atlas_agents/knowledge and then use CoreEvolver to propose improvements to atlas_core.py.

## Acceptance Criteria
### Acceptance Criteria

**1. Knowledge Acquisition: AI Agent Patterns**
- **Verify:** A markdown file (e.g., `ai_agent_patterns.md` or an updated `ai_trends.md`) exists in `/home/chrisj/atlas_agents/knowledge/`.
- **Verify:** The document contains up-to-date research on modern AI agent architectures, such as multi-agent orchestration, reflection loops, dynamic tool-use, and context-window optimization.

**2. Knowledge Acquisition: Next.js & TypeScript Standards**
- **Verify:** A markdown file (e.g., `nextjs_ts_standards.md` or an updated `nextjs_best_practices.md`) exists in `/home/chrisj/atlas_agents/knowledge/`.
- **Verify:** The document details current best practices, specifically focusing on App Router paradigms, React Server Components (RSC), Server Actions, and strict TypeScript typing conventions.

**3. Architectural Synthesis**
- **Verify:** A synthesis step is executed where the newly acquired AI agent patterns are cross-referenced against the current architecture of `bin/atlas_core.py`.
- **Verify:** At least one viable architectural improvement or efficiency optimization is identified for the core engine based on this research.

**4. Core Evolution Proposal & Implementation**
- **Verify:** A new git branch is created specifically for this evolution (e.g., `feat/agent-pattern-optimization`).
- **Verify:** `bin/atlas_core.py` is updated on this branch to incorporate the proposed improvement (e.g., enhancing multi-threaded task handling, refining the prompt injection hierarchy, or adding a JIT tool module).
- **Verify:** The implementation strictly adheres to the **Conservation Principle** (no existing code/features are deleted; obsolete features are disabled via `local_config.json` instead). 
- **Verify:** The code modification passes basic syntax and health checks before being proposed for a merge.

## Architecture
Here is the refined, hardened architectural and execution plan. It directly mitigates the critical security flaws, scalability bottlenecks, and error-handling deficiencies identified in the critique while maintaining high-performance, multi-threaded execution and strict adherence to the Conservation Principle.

### Refined Architectural Plan: Secure Research, Synthesis, and Core Evolution

#### 1. Directory Structure
The operational footprint remains localized but introduces a strict sandboxing environment for runtime validation.

```text
$AGENT_ROOT/
├── knowledge/                        # Sanitized Target for Knowledge Acquisition
│   ├── ai_trends.md                  
│   └── nextjs_best_practices.md      
├── core/
│   └── local_config.json             # Thread-safe target for disabling legacy features
├── bin/
│   ├── atlas_core.py                 # Target for Architectural Synthesis & Evolution
│   ├── api_retry_handler.py          # Enforces network fault tolerance (QUOTA_MANAGER)
│   └── approval_manager.py           # Enforces Governance Controls
└── workspace/
    └── evolution_sandbox/            # Isolated environment for AST manipulation and runtime validation
```

#### 2. Hardened Data Flow Architecture
The process now incorporates strict sanitization, operator governance, and atomic rollbacks.

1.  **Bounded & Resilient Ingestion (Multi-threaded):**
    *   *Network Resilience:* All external data requests are routed through `execute_with_retry` in `bin/api_retry_handler.py` to handle HTTP 429s and timeouts.
    *   *Memory Bounding:* Data streams are strictly chunked (e.g., 4096 tokens max per thread) to prevent OOM crashes.
2.  **Sanitization & Persistence:**
    *   *Injection Defense:* External text is stripped of executable code blocks. Only structural concepts and architectural patterns are extracted and persisted to `knowledge/*.md`.
3.  **Sandboxed Synthesis (Reflection Loop):**
    *   The Synthesizer analyzes `bin/atlas_core.py` within `workspace/evolution_sandbox/`.
    *   AST parsing and injection are wrapped in strict `try/except` blocks to catch `SyntaxError` or `ValueError` during node resolution.
4.  **Governance & Authorization (Mandatory):**
    *   The proposed AST mutation (e.g., adding `JITToolManager`) is packaged as a diff.
    *   Submitted to `ApprovalManager.submit_request()` with a high risk score (e.g., 95.0), pausing execution until `APPROVE` is received from the Telegram operator via `tg_gateway.py`.
5.  **Thread-Safe Evolution & Config Mutation:**
    *   Creates branch `feat/agent-pattern-optimization`.
    *   Applies the approved code mutation to `atlas_core.py`.
    *   Updates `local_config.json` using a `threading.Lock()` (similar to `db_lock`) to prevent race conditions when appending to `"disabled_features": []`.
6.  **Runtime Validation & Atomic Rollback:**
    *   *Syntax Check:* `python3 -m py_compile bin/atlas_core.py`.
    *   *Runtime Sandbox:* Spawns a subprocess to import `atlas_core.py` and instantiate the new class, verifying it doesn't crash on initialization.
    *   *Rollback Protocol:* If validation fails, automatically executes `git reset --hard HEAD` and `git checkout main`, logging the failure.

#### 3. Core Components Involved

*   **Bounded Research Engine:** Utilizes `APIQuotaManager` for network calls and enforces memory chunking. Includes a strict regex-based sanitization layer to neutralize indirect prompt injections.
*   **Sandboxed Synthesizer:** Safely parses the AST of `atlas_core.py` using robust exception handling. Generates code modification proposals rather than applying them directly.
*   **Governance Integrator:** Interfaces with `bin/approval_manager.py` to halt the pipeline and request operator sign-off before any core files are touched.
*   **Atomic CoreEvolver:** 
    *   *Branch Manager:* Executes git operations.
    *   *Config Lock Manager:* Ensures thread-safe IO for `local_config.json`.
    *   *Rollback Controller:* Reverts git state if the runtime validation subprocess exits with a non-zero status.

---

### Proposed Execution Steps

**Step 1: Resilient Knowledge Acquisition**
*   Initialize multi-threaded ingestion using `execute_with_retry`.
*   Apply token-chunking and strip all raw executable code from incoming AI and Next.js research.
*   Write sanitized summaries to `knowledge/ai_trends.md` and `knowledge/nextjs_best_practices.md`.

**Step 2: Sandboxed Synthesis & Proposal Generation**
*   Copy `bin/atlas_core.py` into `workspace/evolution_sandbox/`.
*   Inside a `try/except` block, use the `ast` module to draft the injection of a `ReflectionTaskWrapper` or `JITToolLoader`.
*   Generate a unified diff of the proposed changes.

**Step 3: Governance Checkpoint**
*   Call `ApprovalManager.submit_request(action="Core Code Mutation: JITToolLoader", context=diff_string, risk_score=95.0)`.
*   *Halt execution* until the Telegram operator responds with `APPROVE`.

**Step 4: Thread-Safe Core Evolution**
*   Upon approval, execute `git checkout -b feat/agent-pattern-optimization`.
*   Apply the AST mutation to the live `bin/atlas_core.py`.
*   Acquire an IO lock, read `core/local_config.json`, append deprecated feature flags to `disabled_features`, write to disk, and release the lock.

**Step 5: Runtime Validation & Commit**
*   Run syntax check: `python3 -m py_compile bin/atlas_core.py`.
*   Run sandboxed initialization: `python3 -c "import sys; sys.path.append('bin'); import atlas_core; print('Runtime OK')"`
*   *If success:* `git commit -am "feat: implement JITToolLoader (approved)"`.
*   *If failure:* Execute rollback (`git reset --hard && git checkout main`) and log the exception.
