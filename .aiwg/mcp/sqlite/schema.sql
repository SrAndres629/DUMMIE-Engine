-- SQLite Contract for DUMMIE-Engine
-- Role: ephemeral_structured_store
-- Status: Subordinated to 4D-TES

CREATE TABLE IF NOT EXISTS mcp_runtime_inventory (
    id TEXT PRIMARY KEY,
    server_name TEXT NOT NULL,
    capability_class TEXT,
    last_healthcheck_at TIMESTAMP,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS mcp_policy_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_name TEXT,
    tool_name TEXT,
    intent_type TEXT,
    decision TEXT, -- ALLOW, BLOCK, WARN
    reason TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
