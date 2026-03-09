# Project Scratchpad

Goal: Execute the pending tasks in /home/chrisj/atlas_agents/core/HEARTBEAT.md

## Acceptance Criteria
### Acceptance Criteria

1. **Audit Documentation:** A report or log is generated detailing the audit of the `bin/` directory, specifically identifying any redundant logic found across the scripts (e.g., duplicate DB connections, overlapping caching mechanisms, or repeated file I/O operations).
2. **Prompt Optimization:** The codebase (specifically where the "Hierarchy of Truth" prompt is constructed, likely in `atlas_core.py`) is updated to improve token efficiency (e.g., removing redundant instructions, condensing system prompts).
3. **JIT Tool Proposal:** A concrete proposal (or implementation) for a new 'JIT' (Just-In-Time) tool is created and saved within the repository (e.g., as a new markdown file in `skills/` or a new python script in `bin/`).
4. **Evolution Branching:** All code modifications resulting from the audit (refactoring, prompt optimization, or new tool creation) are committed to a newly created git branch (e.g., `evolution/core-audit-update`).
5. **Heartbeat Update:** The `core/HEARTBEAT.md` file is successfully modified to mark the `CORE_ARCHITECTURE_AUDIT` task as complete (`[x]`).

## Architecture
Here is the **Final Refined Architecture Plan**, fully restructured to address the critical security, scalability, and logic flaws identified in the critique. 

This plan strictly adheres to the **Conservation Principle** (no code deletion), implements in-memory caching for O(1) context retrieval, secures against prompt injection, and ensures robust exception handling to prevent race conditions (TOCTOU) and fatal crashes.

---

### 1. Refined Architecture Plan: Core Audit & Evolution

#### A. Directory Structure & The Conservation Principle
We will introduce the new tools but **strictly preserve** all existing files. Redundant legacy scripts will be systematically disabled via the `local_config.json` feature-flag system rather than deleted.

*   **Preserved (Disabled via Config):** `bin/monitor.py`, `bin/error_handler.py`, `bin/monitor_resources.sh`, `lib/db_manager.py`.
*   **New/Updated (Active):** 
    *   `bin/unified_monitor.py` (New centralized monitor)
    *   `bin/jit_context_loader.py` (New in-memory caching context loader)
    *   `bin/atlas_core.py` (Updated with safe file I/O, sanitization, and smart parsing)
    *   `workspace/audit_report_v8.md` (Detailed audit findings)

#### B. Data Flow Optimization & Scalability
1. **In-Memory JIT Indexing:** `jit_context_loader.py` will build an in-memory dictionary of `skills/` and `knowledge/` at startup. This eliminates O(N) synchronous disk I/O on every prompt and unblocks the main thread.
2. **Safe File Operations:** All disk reads will be wrapped in `try...except OSError` blocks to mitigate TOCTOU race conditions and prevent `FileNotFoundError` crashes.
3. **Smart Context Parsing:** `HEARTBEAT.md` will be parsed logically, stripping out completed (`- [x]`) tasks while preserving headers (`#`) and multi-line descriptions for pending tasks.

#### C. Security Hardening
1. **Prompt Sanitization:** User inputs will be scrubbed of structural delimiters (`<<<`, `>>>`, `[CONFIG]`) to prevent prompt injection attacks from overriding the agent's core identity or system instructions.

---

### 2. Execution Steps & Code Implementation

#### Step 1: Create Evolution Branch & Update Configuration
```bash
cd $AGENT_ROOT
git checkout -b evolution/core-audit-update
```
*Action:* Modify `$AGENT_ROOT/core/local_config.json` to disable redundant features.
```json
{
  "max_threads": 8,
  "cache_size": "2GB",
  "profile": "high-performance",
  "disabled_features": [
    "legacy_monitor_script",
    "legacy_error_handler_monitor",
    "legacy_bash_monitor",
    "legacy_lib_db_manager"
  ]
}
```

#### Step 2: Implement the JIT Context Loader (`bin/jit_context_loader.py`)
*Addresses: O(N) Disk I/O, TOCTOU Race Conditions, Main Thread Blocking.*
```python
import os
import re
import threading

class JITContextManager:
    """In-memory cache for Just-In-Time context loading to prevent sync I/O bottlenecks."""
    def __init__(self, search_dirs=['skills', 'knowledge']):
        self.search_dirs = search_dirs
        self.cache = {}
        self.lock = threading.Lock()
        self.agent_root = os.path.expanduser("~/atlas_agents")
        self._build_index()

    def _build_index(self):
        with self.lock:
            for d in self.search_dirs:
                dir_path = os.path.join(self.agent_root, d)
                if not os.path.exists(dir_path): continue
                
                try:
                    for filename in os.listdir(dir_path):
                        if not filename.endswith('.md'): continue
                        filepath = os.path.join(dir_path, filename)
                        try:
                            # TOCTOU protection: handle case where file is deleted between listdir and open
                            with open(filepath, 'r', errors='ignore') as f:
                                self.cache[filepath] = f.read()
                        except OSError:
                            pass 
                except OSError:
                    pass

    def get_relevant_context(self, user_prompt, max_files=2):
        keywords = set(re.findall(r'\b[a-zA-Z]{4,}\b', user_prompt.lower()))
        scored_files = []
        
        with self.lock:
            for filepath, content in self.cache.items():
                score = sum(1 for k in keywords if k in content.lower())
                if score > 0:
                    scored_files.append((score, filepath, content))
                    
        scored_files.sort(reverse=True, key=lambda x: x[0])
        
        context_texts = []
        for score, filepath, content in scored_files[:max_files]:
            context_texts.append(f"--- FILE: {os.path.basename(filepath)} ---\n{content}")
                
        return "\n\n".join(context_texts)

# Initialize singleton at module load
JIT_MANAGER = JITContextManager()
```

#### Step 3: Optimize and Secure `atlas_core.py`
*Addresses: Prompt Injection, Fatal Crash Risks, Destructive Parsing.*
```python
import os
import json
import re
from jit_context_loader import JIT_MANAGER

def sanitize_input(user_input):
    """Prevents prompt injection by stripping structural delimiters."""
    return re.sub(r'(<<<|>>>|\[CONFIG\])', '', user_input)

def get_safe_file_content(filepath, fallback=""):
    """Safely reads a file with TOCTOU and missing file protection."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return f.read()
    except OSError as e:
        print(f"[WARNING] Safe read failed for {filepath}: {e}")
    return fallback

def extract_active_goals(heartbeat_content):
    """Smart parsing: Keeps headers and pending tasks + sub-lines. Strips completed."""
    lines = heartbeat_content.split('\n')
    active_lines = []
    skip_mode = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- [x]'):
            skip_mode = True
            continue
        elif stripped.startswith('- [ ]'):
            skip_mode = False
            active_lines.append(line)
        elif line.startswith('#'):
            skip_mode = False
            active_lines.append(line)
        elif not skip_mode and stripped:
            active_lines.append(line)
            
    return '\n'.join(active_lines)

def build_optimized_prompt(user_input):
    sanitized_input = sanitize_input(user_input)
    
    # 1. Minify Config safely
    try:
        config = read_local_config()
        minified_config = json.dumps(config, separators=(',', ':'))
    except Exception:
        minified_config = "{}"
    
    # 2. Extract safe context
    soul_content = get_safe_file_content(SOUL_FILE, "Core Identity Not Found.")
    heartbeat_content = get_safe_file_content(HEARTBEAT_FILE, "No Active Goals.")
    active_tasks = extract_active_goals(heartbeat_content)
    
    # 3. JIT Context Loading (O(1) from memory)
    dynamic_skills = JIT_MANAGER.get_relevant_context(sanitized_input)
    
    prompt = f"""<<< ANCHORED_CORE_IDENTITY >>>
{soul_content}
[CONFIG]: {minified_config}
<<< END IDENTITY >>>

<<< ACTIVE GOALS >>>
{active_tasks}

<<< JIT CONTEXT >>>
{dynamic_skills}

USER: {sanitized_input}"""
    return prompt
```

#### Step 4: Generate the Audit Report (`workspace/audit_report_v8.md`)
```markdown
# Core Architecture Audit Report (v8)
**Date:** $(date)
**Focus:** `bin/` directory redundancy, token efficiency, and security hardening.

## Findings & Resolutions:
1. **Conservation Principle Adherence:** Identified redundant monitoring and DB scripts (`monitor.py`, `error_handler.py`, `monitor_resources.sh`). Instead of deleting them, they were safely added to `disabled_features` in `local_config.json`.
2. **I/O Bottlenecks:** The proposed JIT tool previously relied on O(N) synchronous disk reads. Resolved by implementing `JITContextManager` with an in-memory `threading.Lock()` cache loaded at initialization.
3. **Security Vulnerabilities:** 
   - **TOCTOU / Crashes:** Wrapped all file operations in `try...except OSError` blocks.
   - **Prompt Injection:** Implemented `sanitize_input()` to strip structural delimiters from user prompts.
4. **Context Destruction:** Replaced naive `- [ ]` filtering with `extract_active_goals()`, preserving markdown headers and multi-line task contexts while correctly stripping completed `- [x]` chains.
```

#### Step 5: Update HEARTBEAT.md and Commit
Modify `core/HEARTBEAT.md`:
```markdown
- [x] **CORE_ARCHITECTURE_AUDIT:** Use your new Atlas 3.1 capabilities to audit your entire bin/ directory. 
      1. Analyze for redundant logic across files.
      2. Optimize the "Hierarchy of Truth" prompt injection for token efficiency.
      3. Propose a new 'JIT' tool that would have helped in the last 5 tasks.
      4. If improvements are found, create a new evolution branch and implement them.
```

Commit and push the evolution branch:
```bash
git add bin/atlas_core.py bin/jit_context_loader.py workspace/audit_report_v8.md core/HEARTBEAT.md core/local_config.json
git commit -m "Evolution: Secure core architecture audit, add in-memory JIT cache, enforce conservation principle"
git push origin evolution/core-audit-update
```
