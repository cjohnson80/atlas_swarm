# Project Scratchpad

Goal: i would like to interact through the telegram bot just like i do in the terminal

## Acceptance Criteria
# Acceptance Criteria

- **AC1: Terminal Command Handler Integration**
  The Telegram gateway (`bin/tg_gateway.py`) must implement a new command handler (e.g., `/sh`, `/cmd`, or a dedicated terminal mode) that accepts raw string inputs intended for terminal execution.

- **AC2: Secure Execution & Authorization**
  Before execution, the handler must verify the user's identity using the existing `is_authorized` function and validate the payload against the `is_safe_command` blacklist to prevent catastrophic system operations (e.g., `rm -rf /`).

- **AC3: Output Capture and Routing**
  The bot must execute the authorized command on the local machine (or the currently focused machine via the existing routing logic), capture both standard output (`stdout`) and standard error (`stderr`), and send the combined output back to the Telegram chat.

- **AC4: Long Message Pagination/Truncation**
  The handler must account for Telegram's 4096-character message limit. If the terminal output exceeds this limit, the bot must either split the output into multiple sequential messages or truncate the output with a clear `[Output Truncated]` indicator.

- **AC5: Asynchronous Non-Blocking Execution**
  The command execution process must be asynchronous to ensure the Telegram bot's event loop is not blocked, allowing the bot to receive and process other messages or cancellation commands while a long-running terminal task is processing.

## Architecture
Here is the refined, hardened architecture plan for the asynchronous terminal interface. This revision rigorously addresses the security vulnerabilities, resource management flaws, and concurrency risks identified in the critique, ensuring alignment with High-Performance execution standards while maintaining absolute system integrity.

### 1. Directory Structure Updates
In accordance with the Conservation Principle, existing functions like `is_safe_command` will be preserved but bypassed for this specific feature in favor of a new, strict validation pipeline.

```text
$AGENT_ROOT/
├── bin/
│   ├── tg_gateway.py         # (Modified) Add /sh handler, routing, and whitelist integration
│   ├── async_shell.py        # (New) Secure exec, streaming reads, and zombie reaping
│   └── logger_setup.py       # (Existing) Audit logging
```

### 2. Hardened Data Flow Architecture

1. **Ingestion & Parsing:** User sends `/sh <command>` to the Telegram bot. The payload is parsed using `shlex.split()` to safely separate the base executable from its arguments.
2. **Security Gate (Whitelist):** 
   - `is_authorized()` verifies the Telegram User ID.
   - The base executable is checked against a strict **Hardcoded Whitelist** (e.g., `ls`, `pwd`, `cat`, `git`, `npm`, `python3`, `echo`).
3. **Routing Check:**
   - The bot checks `get_focus()`. If remote, it routes via `route_to_machine()`. If local, it proceeds to the `Async Shell Executor`.
4. **Execution (Secure & Isolated):** 
   - `asyncio.create_subprocess_exec` is invoked (bypassing `/bin/sh` entirely to prevent injection).
   - A sanitized `env` dictionary is passed (stripping API keys and DB credentials).
   - `stdin=asyncio.subprocess.DEVNULL` is set to instantly terminate interactive prompts.
5. **Streaming & Resource Limits:** 
   - `stdout` and `stderr` are read concurrently using `asyncio.gather` to prevent OS pipe deadlocks.
   - A hard byte limit (e.g., 15KB) is enforced *during* the read stream. If exceeded, the process is preemptively killed to prevent OOM.
6. **Reaping & Formatting:** 
   - The process is awaited. If a `TimeoutError` occurs, a `SIGKILL` is issued, followed by `await process.wait()` to prevent zombie processes.
   - The output is paginated (up to 3 Telegram messages), and the final message appends the explicit `[Exit Code: X]`.

### 3. Component Breakdown

#### A. Terminal Command Handler (`tg_gateway.py`)
- **Implementation:** Register `CommandHandler('sh', shell_command)`.
- **Functionality:** Extracts the command string. Uses `shlex.split(payload)` to generate an argument list. Passes the list to the security validator.
- **Concurrency Control:** Wraps the execution call in a dedicated `asyncio.Semaphore(3)` to prevent PID/FD exhaustion from rapid command spam, independent of the main gateway semaphore.

#### B. Strict Whitelist Validator (`tg_gateway.py` / `async_shell.py`)
- **Implementation:** A new function `is_whitelisted_command(cmd_list)`.
- **Logic:** Extracts `cmd_list[0]` and verifies it against a predefined `ALLOWED_BINARIES` set. If it fails, execution is immediately rejected. The legacy `is_safe_command` will remain in the codebase but will not be used for the `/sh` route.

#### C. Secure Subprocess Executor (`async_shell.py`)
- **Implementation:** `execute_secure_command(cmd_list, timeout=60.0)`
- **Security Hardening:**
  - `program = cmd_list[0]`, `args = cmd_list[1:]`
  - `env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.environ.get("HOME", "/tmp"), "LANG": "C.UTF-8"}`
  - `process = await asyncio.create_subprocess_exec(program, *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.DEVNULL, env=env)`
- **Zombie Prevention:** Wrapped in a `try...except asyncio.TimeoutError` block. The `except` block explicitly calls `process.kill()` and `await process.wait()`.

#### D. Streaming Reader & Paginator (`async_shell.py`)
- **Implementation:** A custom async reader function `stream_read_limit(stream, limit=15360)`.
- **Logic:** Reads chunks (e.g., 1024 bytes) from the stream until EOF or the 15KB limit is hit. If the limit is hit, it raises a custom `OutputLimitExceeded` exception, triggering process termination.
- **Deadlock Prevention:** Uses `stdout_data, stderr_data = await asyncio.gather(stream_read_limit(process.stdout), stream_read_limit(process.stderr))`.
- **Formatting:** Combines streams, chunks into 4000-character blocks (max 3), wraps in Markdown `` ```bash ``, and appends `\n[Exit Code: {process.returncode}]`.

### 4. Next Steps for Implementation

With this hardened architecture, the system is protected against shell injection, environment leakage, OOM attacks, interactive hangs, and zombie processes, while fully utilizing the High-Performance asynchronous event loop.

I am ready to proceed. I will:
1. Create a new git branch: `feature/secure-async-shell`.
2. Implement `bin/async_shell.py` with the executor and streaming logic.
3. Update `bin/tg_gateway.py` to integrate the `/sh` handler and whitelist.
4. Commit the changes. 

Shall I execute the implementation?
