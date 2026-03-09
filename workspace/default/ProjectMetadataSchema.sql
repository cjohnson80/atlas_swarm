-- SQL Schema for Project Metadata (SQLite compatible)
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    creation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'PAUSED', 'COMPLETE', 'BLOCKED')),
    primary_stack TEXT,
    last_modified DATETIME
);

CREATE INDEX IF NOT EXISTS idx_project_status ON projects(status);

CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    description TEXT NOT NULL,
    priority INTEGER DEFAULT 5,
    is_complete BOOLEAN DEFAULT 0,
    assigned_to TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE INDEX IF NOT EXISTS idx_task_project_id ON tasks(project_id);
-- Optimization Note: For large datasets, consider partitioning or using a dedicated RDBMS, but this structure is optimized for initial local agent use.
