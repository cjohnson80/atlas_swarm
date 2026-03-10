# ATLAS Core Engine: Bottleneck Autopsy & Protocol Formalization

## 1. Bottleneck Autopsy: Sequential Latency & Redundant Verification
Based on telemetry data from `logs/performance_optimizations.md`, the ATLAS core engine suffers from critical cyclomatic inefficiencies that drastically inflate execution latency:

*   **Sequential Verification Latency:** The engine processes state mutations and state verifications as separate, sequential thought-action cycles. For example, executing a command and then running a separate tool call to verify its success adds massive overhead (e.g., 88s latency for simple setup tasks). Verification must be inferred from deterministic execution outputs, not redundant secondary queries.
*   **Context Bloat via Unoptimized I/O:** Reading entire files sequentially for simple redundancy checks (e.g., 83.4s for auditing two files) consumes excessive tokens and processing time. The engine relies heavily on 'heavy lifting' full-file reads where 'light scanning' (grep/AST parsing) would suffice.
*   **Redundant Tool Invocations:** Multiple tool calls are used where a single, bundled execution would suffice. The engine fails to leverage atomic operations, leading to high attempt counts and latency (e.g., 184.1s for a research task over 3 attempts).

## 2. Protocol Specification: Single-Source Truth (SST)
To mathematically prevent state-drift and eliminate redundant verification loops, the SST protocol is defined as follows:

*   **O(1) State Resolution:** System state must be queried exactly once per execution cycle and cached locally within the execution context.
*   **Immutable State Management:** Once state is read, it is treated as immutable for the duration of the operational cycle. Any mutations must yield a new state object, rather than modifying the existing one in place.
*   **Strict Separation of Concerns:** State mutation (writing to disk, executing commands) must be strictly separated from state verification. Verification must rely entirely on the deterministic output of the mutation operation (e.g., exit codes, stdout streams) rather than redundant, post-execution read operations.

## 3. Protocol Specification: Atomic Delivery
To ensure idempotent, all-or-nothing execution pipelines and eradicate partial state commits, the Atomic Delivery protocol mandates:

*   **Zero-Tolerance for Partial Commits:** All related state mutations (e.g., writing multiple files, executing setup commands) must be bundled into a single, atomic transaction.
*   **Execution Bundling:** Shell executions must use logical AND (`&&`) to chain commands, ensuring that failure at any step halts the entire pipeline immediately and returns a single, deterministic error code. Multiple `run_shell` or `write_file` calls for a single logical operation are strictly prohibited.
*   **Idempotency Guarantee:** Every operational pipeline must be structurally safe to run multiple times without changing the result beyond the initial application. State must be overwritten deterministically, never appended blindly.
