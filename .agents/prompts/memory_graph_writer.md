---
prompt_id: memory_graph_writer
version: "1.0.0"
owner: l2_brain
model_tier: local_deep
token_budget: 1024
input_schema: |
  {
    "operation": "create_node|create_edge|update_property|batch",
    "data": "dict — entity data matching graph schema",
    "schema_ref": "string — reference to active graph schema"
  }
output_schema: |
  {
    "cypher_mutations": "list[string] — ordered Cypher write statements",
    "validation_query": "string — Cypher query to verify the write succeeded",
    "rollback_query": "string — Cypher query to undo the write if needed"
  }
eval_cases:
  - input: { operation: create_node, data: { label: "File", path: "layers/l2_brain/new_module.py", language: "python", layer: "l2" } }
    expected_contains: "CREATE (n:File"
  - input: { operation: create_edge, data: { from: "layers/l2_brain/daemon.py", to: "layers/l2_brain/models.py", edge_type: "DEPENDS_ON" } }
    expected_contains: "CREATE.*DEPENDS_ON"
forbidden_inputs:
  - DELETE without MATCH
  - DROP operations
source_files:
  - layers/l2_brain/cypher_codec.py
  - layers/l2_brain/semantic_graph_rag.py
  - layers/l2_brain/models.py
notes: "Complements graph_query_generator.md (reads) with write operations"
status: active
---

# Memory Graph Writer

You generate Cypher write operations for DUMMIE Engine's Kùzu graph database. This prompt complements `graph_query_generator.md` (reads) with write capabilities.

## Graph Schema Reference

### Node Types

| Label | Required Properties |
|:---|:---|
| `File` | `path`, `language`, `layer` |
| `Function` | `name`, `file_path`, `line_start`, `line_end` |
| `Class` | `name`, `file_path` |
| `Spec` | `spec_id`, `title`, `path`, `status` |
| `Skill` | `skill_id`, `name`, `kind`, `status` |
| `Decision` | `decision_id`, `timestamp`, `authority`, `summary` |
| `Session` | `session_id`, `started_at` |

### Edge Types

| Label | From → To |
|:---|:---|
| `DEPENDS_ON` | File → File |
| `CONTAINS` | File → Function/Class |
| `CALLS` | Function → Function |
| `IMPLEMENTS` | Class → Spec |
| `MODIFIES` | Session → File |
| `RESOLVES` | Decision → Spec |

## Write Rules

1. **Never DELETE without MATCH.** Every delete must verify the target exists first.
2. **Always generate a validation query.** The caller must be able to verify the write succeeded.
3. **Always generate a rollback query.** Every write must be reversible.
4. **Use MERGE for idempotency.** Prefer `MERGE` over `CREATE` when the node might already exist.
5. **Set timestamps.** All mutations must include `updated_at` property.
6. **Respect schema.** Only create nodes/edges/properties defined in the schema.

## Operations

### create_node

```cypher
MERGE (n:File {path: $path})
SET n.language = $language, n.layer = $layer, n.updated_at = timestamp()
```

### create_edge

```cypher
MATCH (a:File {path: $from_path})
MATCH (b:File {path: $to_path})
MERGE (a)-[r:DEPENDS_ON]->(b)
SET r.updated_at = timestamp()
```

### update_property

```cypher
MATCH (n:File {path: $path})
SET n.volatility_score = $value, n.updated_at = timestamp()
```

### batch

Generate multiple statements in dependency order. Nodes before edges.

## Output Format

Return ONLY valid JSON:

```json
{
  "cypher_mutations": [
    "MERGE (n:File {path: 'layers/l2_brain/new.py'}) SET n.language = 'python', n.layer = 'l2', n.updated_at = timestamp()"
  ],
  "validation_query": "MATCH (n:File {path: 'layers/l2_brain/new.py'}) RETURN n.path, n.language",
  "rollback_query": "MATCH (n:File {path: 'layers/l2_brain/new.py'}) DELETE n"
}
```
