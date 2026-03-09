# System-Wide Approval Workflow: Risk Assessment Logic Specification

This section defines the criteria for automatically assigning a Risk Level to proposed operations, dictating whether the human operator must intervene via Telegram.

## 1. Risk Categorization Matrix

Operations are categorized based on their potential impact, which is determined by the tool being invoked and the nature of the operation.

| Operation Type | Specific Action (Keywords/Patterns) | Default Risk Level | Rationale |
| :--- | :--- | :--- | :--- |
| **System Execution** | `run_shell` involving `rm`, `mv` (to system paths), `chmod`, `chown`, or execution of non-whitelisted binaries (e.g., network tools). | **HIGH** | Direct system modification, potential for data destruction or security compromise. |
| **System Execution** | `run_shell` involving benign operations (e.g., `ls`, `cat` on non-sensitive files, running agent internal scripts). | **LOW** | Informational or routine maintenance; low impact. |
| **File I/O** | `write_file` or `read_file` targeting core agent configuration (`local_config.json`, `$AGENT_ROOT`), or source code (`$REPO_ROOT`). | **HIGH** | Modification or exposure of core logic, secrets, or operational parameters. |
| **File I/O** | `write_file` or `read_file` targeting ephemeral workspace directories (`/workspace/default/`). | **MEDIUM** | Affects current task state, but generally recoverable or isolated. |
| **Git Operations** | `run_shell` involving `git push`, `git checkout` to external branches, or modifying `.git` directory contents. | **HIGH** | Externalizing state or changing repository history/source. |
| **Git Operations** | `run_shell` involving `git status`, `git log`, or local commits within the current task branch. | **LOW** | Internal development workflow monitoring. |

## 2. Risk Threshold Configuration

The system uses a global threshold defined in `local_config.json`. An operation is flagged for approval if its calculated Risk Level meets or exceeds this threshold.

**Default Threshold:** MEDIUM (i.e., any MEDIUM or HIGH operation requires approval).

## 3. Authorization Check: Telegram User ID Validation

To prevent unauthorized approvals, the `ApprovalManager` must strictly validate the source of the approval command.

1.  **Whitelist Storage:** A list of authorized operator Telegram IDs (`allowed_tg_ids`) must be stored securely (ideally encrypted, but initially in `local_config.json`).
2.  **Validation Logic:** When `tg_gateway.py` receives an incoming message, it extracts the sender's ID (`incoming_tg_id`).
3.  **Gate Check:** The `ApprovalManager` refuses to process the instruction unless `incoming_tg_id` is present in the `allowed_tg_ids` list.
4.  **Logging:** Any attempt to approve an action by an unauthorized ID must be logged as a **SECURITY ALERT** and immediately reported to the primary operator channel without executing the proposed action.