# Project Scratchpad

Goal: try  to find out why the telegram bot isnt responding

## Acceptance Criteria
### Acceptance Criteria

- **AC 1: Log Inspection**
  - Examine `logs/audit.log` and `logs/atlas_core.log` for any stack traces, errors, or warnings originating from `TG_GATEWAY`.
  - Specifically check for the `SECURITY CRITICAL: TELEGRAM_USER_ID not set in .env!` or `UNAUTHORIZED ACCESS ATTEMPT` log entries, which indicate authorization rejections.

- **AC 2: Environment Variable Verification**
  - Verify that a `.env` file exists and is accessible to the `tg_gateway.py` process.
  - Confirm that a valid `TELEGRAM_BOT_TOKEN` is set.
  - Confirm that `TELEGRAM_USER_ID` is set and exactly matches the Telegram ID of the user attempting to send commands.

- **AC 3: Process Health Check**
  - Verify that the `tg_gateway.py` process is currently running and has not silently crashed or been terminated by the OS (e.g., verify via `ps aux | grep tg_gateway.py`).
  - Ensure the `celeron_watchdog` memory management loop hasn't stalled the async event loop.

- **AC 4: Network and API Reachability**
  - Confirm that the host machine (`chris-laptop-dev`) has active internet access and can successfully reach `api.telegram.org` without firewall or DNS blocking.

- **AC 5: Root Cause Documentation & Remediation**
  - Document the explicit reason for the bot's failure to respond.
  - Apply the necessary fix (e.g., updating environment variables, correcting a syntax error, or restarting the service).
  - Prove resolution by successfully receiving a response from the bot to a standard command (e.g., a project command) from the authorized Telegram account.

## Architecture
Here is the refined, secure, and highly scalable architecture plan for the Telegram Gateway (`tg_gateway.py`). This blueprint directly addresses the identified critical vulnerabilities, performance bottlenecks, and architectural flaws.

---

# Refined Telegram Gateway Architecture Blueprint (v2.0)

## 1. Architectural Upgrades & Security Posture

### A. Zero-Trust Security & Input Validation
*   **Strict Whitelisting:** The flawed command blacklist is replaced with a strict **Action Whitelist**. The bot will no longer accept arbitrary shell commands. It will only accept predefined parameterized actions (e.g., `["status", "restart", "deploy", "ping"]`).
*   **Path Traversal Prevention:** All incoming `target_name` variables will be strictly sanitized using regex (`^[a-zA-Z0-9_-]+$`) before being interpolated into file paths.
*   **Cryptographic IPC (HMAC-SHA256):** To prevent unauthenticated Git-based IPC injection, all JSON payloads written to `mailbox/` will be cryptographically signed using a shared `IPC_SECRET`. The receiving machine will drop any payload with an invalid signature.
*   **Subprocess Hardening:** `shell=True` is strictly forbidden. All system calls will use parameterized argument lists to eliminate command injection vectors.

### B. High-Concurrency & Non-Blocking I/O
*   **Async Subprocesses:** Synchronous `subprocess.run` calls (like Git pushes/pulls) block the Python event loop, causing the bot to freeze for all users during network I/O. These will be replaced with `asyncio.create_subprocess_exec()`, allowing the bot to handle hundreds of concurrent requests seamlessly.

### C. Robustness & Environment Management
*   **Explicit Dependency Loading:** `python-dotenv` will be integrated to load `.env` variables programmatically, removing reliance on fragile shell configurations.
*   **Strict Error Handling:** Bare `except: pass` blocks will be removed. JSON decoding errors will be explicitly caught, logged to `audit.log`, and gracefully handled to account for partial file writes during Git pulls.

---

## 2. Implementation Blueprint (`tg_gateway.py` Refactor)

### Step 1: Environment & Dependency Setup
Add `python-dotenv` to `requirements.txt` and update the top of `tg_gateway.py`:
```python
import os
import re
import json
import time
import hmac
import hashlib
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables securely
load_dotenv(os.path.expanduser('~/atlas_agents/.env'))

ALLOWED_USER_ID = os.getenv('TELEGRAM_USER_ID')
IPC_SECRET = os.getenv('IPC_SECRET', 'default_insecure_secret_change_me').encode()
```

### Step 2: Core Security Utilities
Implement sanitization, whitelisting, and cryptographic signing:
```python
ALLOWED_ACTIONS = {"status", "ping", "restart", "update", "deploy"}

def sanitize_target_name(target_name: str) -> bool:
    """Prevents Path Traversal and Injection."""
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", target_name))

def generate_signature(payload_dict: dict) -> str:
    """Generates an HMAC-SHA256 signature for the payload."""
    payload_str = json.dumps(payload_dict, sort_keys=True)
    return hmac.new(IPC_SECRET, payload_str.encode(), hashlib.sha256).hexdigest()
```

### Step 3: Non-Blocking Subprocess Execution
Create a helper for async Git operations to free up the event loop:
```python
async def async_git_command(*args, cwd=REPO_PATH):
    """Executes git commands asynchronously without blocking the event loop."""
    process = await asyncio.create_subprocess_exec(
        'git', *args,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logger.error(f"Git command failed: {stderr.decode().strip()}")
    return process.returncode == 0
```

### Step 4: Secure & Asynchronous Command Routing
Refactor `route_to_machine` to use the new security and async utilities:
```python
async def route_to_machine(target_name: str, action: str, update):
    """Securely mails a command to another machine via Git."""
    if not sanitize_target_name(target_name):
        await update.message.reply_text("❌ Security Error: Invalid target machine name.")
        return
        
    if action not in ALLOWED_ACTIONS:
        await update.message.reply_text(f"❌ Security Error: Action '{action}' is not whitelisted.")
        return

    status_msg = await update.message.reply_text(f"[{MY_HOSTNAME}] Routing '{action}' to {target_name}...")

    cmd_file = os.path.join(MAILBOX_PATH, f"{target_name}_cmd.json")
    
    # Construct and sign payload
    payload = {
        "action": action,
        "chat_id": update.message.chat_id,
        "timestamp": time.time()
    }
    payload["signature"] = generate_signature(payload)

    # Write payload
    with open(cmd_file, 'w') as f:
        json.dump(payload, f)

    # Async Git Push
    await async_git_command("add", "mailbox/")
    await async_git_command("commit", "-m", f"Mailbox: {action} for {target_name}")
    await async_git_command("push", "origin", "main")

    await status_msg.edit_text(f"[{MY_HOSTNAME}] Command queued for {target_name}. Awaiting response...")

    # Async Polling with specific error handling
    res_file = os.path.join(MAILBOX_PATH, f"{target_name}_res.json")
    for _ in range(12): # 60s timeout
        await asyncio.sleep(5)
        await async_git_command("pull", "origin", "main")
        
        if os.path.exists(res_file):
            try:
                with open(res_file, 'r') as f:
                    res_data = json.load(f)
                
                # Verify incoming signature (assuming receiver signed the response)
                incoming_sig = res_data.pop("signature", None)
                if incoming_sig != generate_signature(res_data):
                    logger.warning(f"Invalid signature on response from {target_name}")
                    continue

                await status_msg.edit_text(f"[{target_name}]\n{res_data.get('result', 'Success')}")
                
                # Cleanup
                os.remove(res_file)
                if os.path.exists(cmd_file): os.remove(cmd_file)
                await async_git_command("add", "mailbox/")
                await async_git_command("commit", "-m", f"Mailbox: cleanup {target_name}")
                await async_git_command("push", "origin", "main")
                return
                
            except json.JSONDecodeError as e:
                logger.warning(f"Partial read or corrupted JSON from {target_name}: {e}. Retrying next tick.")
            except Exception as e:
                logger.error(f"Unexpected error processing response: {e}")

    await status_msg.edit_text(f"[{MY_HOSTNAME}] Timeout: {target_name} did not respond.")
```

*Note: The truncated `list_` function at the bottom of the original file must be removed or completed (e.g., `async def list_projects(update, context): ...`) to prevent `SyntaxError` crashes on startup.*

---

## 3. Secure Deployment & Diagnostic Plan

To safely deploy and verify the gateway, execute the following steps. **Do not use `echo` to write secrets.**

### Step 1: Secure Credential Management
Use a text editor (`nano` or `vim`) to securely create the `.env` file, preventing token leakage into `.bash_history`.
```bash
# 1. Create the file and restrict permissions IMMEDIATELY
touch ~/atlas_agents/.env
chmod 600 ~/atlas_agents/.env

# 2. Open the file in an editor
nano ~/atlas_agents/.env
```
*Add the following lines to the file, save, and exit:*
```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token
TELEGRAM_USER_ID=your_actual_user_id
IPC_SECRET=generate_a_strong_random_string_here
```

### Step 2: Install Dependencies
Ensure the new `.env` loader is installed:
```bash
pip install python-dotenv
```

### Step 3: Syntax Verification
Before launching, ensure the file is not truncated and contains valid Python:
```bash
python3 -m py_compile ~/atlas_agents/bin/tg_gateway.py
```
*(If this returns nothing, the syntax is valid. If it throws an `EOFError`, fix the truncated `list_` function).*

### Step 4: Process Execution & Monitoring
Start the bot and monitor the primary audit log for successful initialization:
```bash
# Start the bot in the background
python3 ~/atlas_agents/bin/tg_gateway.py &

# Monitor the logs for immediate errors or Auth warnings
tail -f ~/atlas_agents/logs/audit.log
```
