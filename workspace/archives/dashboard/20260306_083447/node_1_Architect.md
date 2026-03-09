# ARCHITECTURE DESIGN: Telegram Terminal Integration (`/sh`)

## 1. INGRESS & ZERO-TRUST AUTHORIZATION (The Gatekeeper)
Every incoming `/sh` command is treated as a hostile payload. The Gateway enforces a strict perimeter before any parsing occurs.

**Flow:**
1. **Message Reception:** The async event loop (via `python-telegram-bot`) receives the `Update`.
2. **Identity Verification:** Extracts `update.effective_user.id`. Matches strictly against `ALLOWED_USER_ID` loaded from the secure `.env` file. 
3. **Rejection Protocol:** If unauthorized, the request is dropped immediately. A high-priority warning is logged (`UNAUTHORIZED ACCESS ATTEMPT`) to the audit trail. No feedback is provided to the attacker to prevent probing.
4. **Command Sanitization:** The raw payload undergoes a heuristic check against a predefined blacklist (e.g., fork bombs `:(){ :|:& };:`, arbitrary destructive commands `rm -rf /`).

## 2. CONTEXTUAL ROUTING (The Dispatcher)
The system operates within a distributed mesh. The Dispatcher determines *where* the command should execute based on the operator's current "focus".

**Flow:**
1. **State Resolution:** Reads the global state from `$AGENT_ROOT/core/current_focus.json` to determine the target hostname.
2. **Local vs. Remote Branching:**
   - **If Target == `MY_HOSTNAME`:** Routes directly to the Local Execution Engine.
   - **If Target != `MY_HOSTNAME`:** Initiates the Asynchronous Mailbox Protocol.
3. **Remote Routing (Mailbox Protocol):**
   - Serializes the command, `chat_id`, and `timestamp` into a JSON payload.
   - Writes to `$REPO_ROOT/mailbox/<target_name>_cmd.json`.
   - Executes a git commit and push to the central synchronization repository.
   - Enters a polling loop (up to a 60s timeout), pulling the repo to check for `<target_name>_res.json`.

## 3. SECURE LOCAL EXECUTION (The Sandbox)
Commands executed locally must be sandboxed to prevent hanging the main Telegram event loop or creating zombie processes.

**Flow:**
1. **Process Isolation:** Spawns a subprocess using `asyncio.create_subprocess_shell`. The process is launched with a new session ID (`os.setsid` via `preexec_fn`) so that the entire process tree can be terminated if necessary.
2. **Stream Capture:** Attaches async pipes to `stdout` and `stderr` to capture output non-blockingly.
3. **Timeout Enforcement:** Wraps the execution in `asyncio.wait_for(..., timeout=MAX_EXEC_TIME)`. If the timeout is breached, a `SIGTERM` (followed by `SIGKILL` if ignored) is sent to the process group.
4. **State Feedback:** Immediately replies to the user with a transient message: `[MY_HOSTNAME] Executing...` to acknowledge receipt.

## 4. TELEMETRY & OUTPUT FORMATTING (The Presenter)
Telegram has strict constraints (4096 characters per message, specific MarkdownV2 escaping rules). The Presenter ensures data is delivered reliably and legibly.

**Flow:**
1. **Stream Aggregation:** Combines `stdout` and `stderr` into a single chronological buffer. Prepends the exit code if non-zero.
2. **Size Evaluation & Chunking:**
   - **< 4000 chars:** Wraps the output in a Markdown code block (```bash ... ```) and edits the initial "Executing..." message.
   - **> 4000 chars:** Truncates the message with a warning (`...[OUTPUT TRUNCATED]...`). The full unadulterated output is written to a temporary file (`/tmp/cmd_output.txt`) and uploaded back to the user via Telegram's `send_document` API.
3. **Cleanup:** Removes any temporary files and, if part of a remote execution, deletes the mailbox request/response files and commits the cleanup to the repository.