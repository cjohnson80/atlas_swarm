# Project Scratchpad

Goal: thats great! you can always upgrade the shell interface at any time also. I can't interact with you through telegram still. i would like to be able to type like this and have you answer and perform tasks too

## Acceptance Criteria
# Acceptance Criteria

- **AC 1: CLI Interface Creation:** A new interactive terminal script (e.g., `bin/cli_gateway.py` or `bin/agent_shell.py`) is created to serve as an alternative to the Telegram gateway.
- **AC 2: Continuous Interactive Loop:** The script implements a continuous Read-Eval-Print Loop (REPL) that allows the user to type multiple, consecutive prompts or commands without needing to restart the application.
- **AC 3: Core Engine Integration:** User inputs from the shell are successfully routed to the `AtlasSwarm` core engine (or the equivalent task execution pipeline) to generate AI responses and execute requested tasks.
- **AC 4: Task Execution & Feedback:** The interface supports triggering file system changes, script executions, or research tasks, and prints the operational output (success, failure, or data) directly back to the terminal.
- **AC 5: Graceful Termination:** The shell interface handles exit commands (e.g., `exit`, `quit`) and keyboard interrupts (`Ctrl+C`) gracefully, terminating the session without throwing unhandled exceptions.

## Architecture
Here is the refined and hardened architectural plan for the **AtlasSwarm Interactive CLI Gateway**. It fully addresses the security, concurrency, and resilience flaws identified in the critique while maintaining optimization for our High-Performance hardware profile.

### 1. Directory Structure & Permission Integration
The new interface will sit alongside the existing components in the `bin/` directory. All new state and log files will strictly enforce `umask 077` and `600` (`-rw-------`) permissions to prevent unauthorized local access.

```text
$AGENT_ROOT/
├── bin/
│   ├── atlas_core.py         <-- Core AGI Engine
│   ├── db_manager.py         <-- Thread-safe Database Manager
│   ├── error_handler.py      <-- Global Exception Handling
│   └── cli_gateway.py        <-- NEW: Interactive Shell Interface (Target)
├── core/
│   └── cli_history.log       <-- NEW: Session history (Strict 600 permissions)
├── logs/
│   └── cli_gateway.log       <-- NEW: Dedicated CLI logging (Strict 600 permissions)
└── workspace/                <-- Execution target for file/script tasks
```

### 2. Component Architecture (Revised)

**A. Security & Access Controller (NEW)**
*   **UID Verification:** On boot, the CLI verifies that the UID of the executing user exactly matches the owner of `$AGENT_ROOT`. If there is a mismatch, the process immediately aborts.
*   **Permission Enforcement:** Sets `os.umask(0o077)` globally at script initialization to guarantee all newly created files (logs, history) default to secure permissions.

**B. REPL Controller (Read-Eval-Print Loop)**
*   **Responsibility:** Maintains the continuous `while True` loop and handles session lifecycle.
*   **Resilient Termination:** Wraps the input prompt in a `try/except` block catching both `KeyboardInterrupt` (Ctrl+C) and `EOFError` (Ctrl+D) to ensure graceful, stack-trace-free exits.
*   **Crash Prevention:** Utilizes `error_handler.safe_execute` (or a localized generic `Exception` catch) around the core execution block to ensure API timeouts or parsing failures simply log the error to `cli_gateway.log` and return the user to the `> ` prompt.

**C. Command Parser & Router**
*   **Responsibility:** Differentiates between local shell meta-commands, AI prompts, and malicious inputs.
*   **Command Sandboxing:** Implements an `is_safe_command()` filter (mirroring `tg_gateway.py`) to intercept and block catastrophic local shell commands (e.g., `rm -rf /`, fork bombs) before they reach the execution engine.
*   **Meta-commands:** Intercepts `/exit`, `/clear`, or `/status` for instant local execution.

**D. MAS Adapter (Core Engine Bridge)**
*   **Responsibility:** Initializes and interacts with the `AtlasSwarm` core.
*   **Thread-Safe DB Integration:** Bypasses direct DuckDB/SQLite connections to avoid lock contention with background processes. It routes all memory/state writes through the `DatabaseManager` (`bin/db_manager.py`) thread-safe write queue.
*   **Rolling Context Window:** To prevent memory leaks during long-lived sessions, the local history array is capped (e.g., last 10 turns). Older context is either truncated or summarized before being passed to the core engine.

**E. Governance & Audit Integration (NEW)**
*   **Responsibility:** Maintains an immutable audit trail for high-risk actions executed via the CLI.
*   **Implementation:** Captures the local OS username (`os.getlogin()` or `pwd.getpwuid(os.getuid()).pw_name`) to use as the `actor_id`. Routes all significant execution decisions through `skills.governance_logger.log_governance_decision()` to ensure CLI actions are audited identically to Telegram-approved actions.

**F. Output Formatter & Feedback Loop**
*   **Responsibility:** Captures the AI's response and any stdout/stderr from executed tasks.
*   **Styling:** Utilizes existing ANSI color codes (`C_CYAN`, `C_GREEN`, `C_RED` for errors) to visually separate user input, AI thought processes, tool executions, and final outputs.

### 3. Data Flow

1.  **Initialization:** User executes `python3 bin/cli_gateway.py`. The Security Controller verifies the UID and sets the umask. The script connects to the `DatabaseManager` and spins up the `AtlasSwarm` core.
2.  **Input Phase:** The REPL prompts the user. User types a command.
3.  **Evaluation Phase:**
    *   The Parser runs `is_safe_command()`. If malicious, it rejects the input and logs a security warning.
    *   If safe, it checks for meta-commands.
    *   If it's a standard prompt, the MAS Adapter appends it to the Rolling Context Window.
4.  **Execution & Governance Phase:**
    *   The execution is wrapped in a `try/except Exception` block.
    *   If the core decides to execute a high-risk tool (e.g., file modification, script execution), it logs the action via `governance_logger` using the OS username as the `actor_id`.
    *   State changes are queued via `DatabaseManager.execute_write()`.
5.  **Print Phase:** Output Formatter prints the formatted response to the terminal.
6.  **Loop/Termination:** The system returns to Step 2. If the user hits `Ctrl+C` or `Ctrl+D`, the REPL Controller intercepts the signal, flushes the DB queue, and safely exits.

### Next Steps for Implementation
With this hardened architecture established, I am ready to implement `bin/cli_gateway.py`. The implementation will strictly adhere to our High-Performance profile guidelines, ensuring multi-threaded DB access and efficient memory management via the rolling context window. 

Awaiting your authorization to write the codebase.
