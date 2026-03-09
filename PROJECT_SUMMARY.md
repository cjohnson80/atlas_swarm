# ATLAS: System Architecture & Workspace Protocol (Streamlined)

This document outlines the architectural components, data flows, and organization of the ATLAS Elite Swarm.

## 1. THE IDENTITY BOUNDARY
ATLAS maintains a clear separation between its internal reasoning engine and client projects.

### System Space (Identity)
- **Engine (`bin/`):** Logic core (`atlas_core.py`), API gateways, and system tools.
- **Identity (`core/`):** Behavioral protocol (`SOUL.md`), configuration (`local_config.json`), and goal tracking.
- **Frontend (`frontend/`):** Next.js 15 Web Interface.
- **Capabilities (`skills/`):** Atomic skill modules.
- **Knowledge (`knowledge/`):** Research data and best practices.
- **The Vault (`library/`):** Component library and project blueprints.
- **Persistence (`memory/`):** Persistent DuckDB storage and mission logs.
- **Maintenance (`scripts/`):** Utility scripts for benchmarks and integrity checks.
- **Validation (`tests/`):** Tests and environment mocks.

### Mission Space (Workspace)
- **Projects (`workspace/`):** Isolated project directories.
- **Archives (`workspace/archives/`):** Historical mission data and dated run folders.

## 2. KEY DATA FLOWS
1. **Command:** Received via CLI, Telegram, or Web UI.
2. **Triage:** Atlas decides if the input is a TASK or CHAT.
3. **Execution:** Specialized agents operate within a mission directory in `workspace/`.
4. **Learning:** High-value patterns are extracted and saved to `library/`.
5. **Persistence:** All state and memory are routed through `bin/db_manager.py` to `memory/`.

## 3. CORE TECHNOLOGY STACK
*   **Engine:** Python 3.14 (Async/Multithreaded).
*   **Intelligence:** Gemini 1.5 Pro.
*   **Persistence:** DuckDB + Polars.
*   **Web Skin:** Next.js 15 + FastAPI.
*   **DevOps:** Vercel CLI, GitHub CLI.

This structure ensures ATLAS remains a high-performance, self-improving architect with a clean, manageable workspace.