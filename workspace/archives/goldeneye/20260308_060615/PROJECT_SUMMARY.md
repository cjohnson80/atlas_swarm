# Project Scratchpad

Goal: Execute the pending tasks in /home/chrisj/atlas_agents/core/HEARTBEAT.md

## Acceptance Criteria
### Acceptance Criteria

**1. Task Extraction & Parsing**
* The file `core/HEARTBEAT.md` (or absolute path `/home/chrisj/atlas_agents/core/HEARTBEAT.md`) is successfully read.
* All pending tasks, directives, or error states documented within the file are explicitly identified and logged for execution.

**2. Strict Spatial Isolation & Protocol Adherence**
* Tasks pertaining to the active mission are executed strictly within the `workspace/goldeneye` directory.
* Tasks pertaining to system health or core evolution are executed within the System Space (`bin/`, `core/`, `skills/`) without contaminating the client workspace.
* No existing, functioning features are deleted; deprecation protocols are followed if components are deemed obsolete.

**3. Task Execution & Verification**
* Every identified task is executed to completion.
* Verifiable proof of completion is obtained for each task (e.g., successful execution of `npm run build`, zero linting/type errors, passing test suites, or verified live endpoints).
* If a task requires a new tool, the Dynamic Tool Synthesis protocol is correctly followed and the tool is verified to work.

**4. State Reconciliation & Reporting**
* Upon completion of all tasks, `core/HEARTBEAT.md` is updated to reflect the resolved status of the pending items (or a detailed status report is generated confirming execution).
* The final system state is verified to be stable, with no new regressions introduced during task execution.

## Architecture
Critique integrated. Spatial isolation enforced. System Space (`core/`) is strictly off-limits for mission-specific tactical extraction. The mission state is encapsulated entirely within the `workspace/goldeneye/` boundary.

Redirecting sensors to the Mission Space sandbox to extract the latest architectural blueprints and execution status for GOLDENEYE. 

Strategy locked. Executing surgical read on the project summary and status report to establish the operational baseline.

```json
[
  {"name": "read_file", "arguments": {"file_path": "workspace/goldeneye/PROJECT_SUMMARY.md"}},
  {"name": "read_file", "arguments": {"file_path": "workspace/goldeneye/research/STATUS_REPORT.md"}}
]
```
