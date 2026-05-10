# DSM (Dummie Swarm Manifest) v2.0 Specification

The Swarm Manifest allows defining complex agent workflows without recompiling the L0 Overseer.

## Schema

```yaml
version: "2.0"
swarm_id: string       # Unique identifier for this swarm instance
meta:
  goal: string         # High level objective
  max_iterations: int  # Safety break for loops

graph:
  nodes:
    - id: string       # Unique node ID in this graph
      type: string     # Registered Node Type (ANALYST, EXECUTOR, REVIEWER, etc.)
      config: object   # Node-specific configuration (prompts, tools, etc.)
      
  edges:
    - from: string     # Source Node ID
      to: string       # Target Node ID
      condition: string # (Optional) Logical condition for transition
```

## Registered Node Types

### `ANALYST`
- **Purpose**: Map the problem space and decide next steps.
- **Config**:
  - `focus`: string (e.g., "code", "architecture", "security")
  - `depth`: int

### `EXECUTOR`
- **Purpose**: Perform actions using MCP tools.
- **Config**:
  - `agent_id`: string
  - `capabilities`: list of strings (tool categories)

### `REVIEWER`
- **Purpose**: Validate results and calculate friction.
- **Config**:
  - `criteria`: list of strings
  - `threshold`: float (0.0 to 1.0)
