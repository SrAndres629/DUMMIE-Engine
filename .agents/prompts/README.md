# DUMMIE Engine — Canonical Prompt Registry

This directory contains the **14 canonical prompts** that define how DUMMIE Engine's agents think, act, and collaborate.

## Prompt Index

### Identity & Governance (static, loaded once per session)

| Prompt | Tier | Purpose |
|:---|:---|:---|
| `sys_identity.md` | any | Who the agent is. Name, architecture, roles, constraints. |
| `workspace_rules.md` | any | How to operate. Execution protocol, blocked paths, diffs. |
| `truth_policy.md` | any | How to verify claims. Evidence rules, sources of truth. |

### Router & Preprocessing (per-task, local)

| Prompt | Tier | Purpose |
|:---|:---|:---|
| `router_classifier.md` | local_fast | Classify task complexity → model tier. |
| `local_sanitizer.md` | local_deep | Clean prompt, extract intent, detect layers. |
| `local_context_compressor.md` | local_deep | Compress RAG/graph/memory results for cloud. |

### Cloud Execution (on-demand, paid)

| Prompt | Tier | Purpose |
|:---|:---|:---|
| `cloud_architect_planner.md` | cloud_prem | Design architecture, create implementation plans. |
| `cloud_code_mutator.md` | cloud_std | Generate precise code diffs and tests. |

### Orchestration & Tools (per-task, local)

| Prompt | Tier | Purpose |
|:---|:---|:---|
| `agent_orchestrator.md` | local_deep | Decompose mission into task DAG with role assignments. |
| `skill_mcp_executor.md` | local_deep | Generate exact MCP tool invocation arguments. |

### Security & Audit (per-mutation, local)

| Prompt | Tier | Purpose |
|:---|:---|:---|
| `security_validator.md` | local_deep | Audit diffs for injections, path traversal, policy violations. |
| `lifecycle_auditor.md` | local_deep | Audit agent/skill/MCP creation and downloads. |

### Knowledge & Memory (per-query, local)

| Prompt | Tier | Purpose |
|:---|:---|:---|
| `graph_query_generator.md` | local_deep | Translate natural language → Cypher read queries. |
| `memory_graph_writer.md` | local_deep | Generate Cypher write/mutation operations. |

## Token Distribution

| Tier | Prompts | Cloud Cost |
|:---|---:|:---|
| `local_fast` | 1 | $0 |
| `local_deep` | 8 | $0 |
| `cloud_std` | 1 | paid |
| `cloud_prem` | 1 | paid |
| `any` (static) | 3 | varies |
| **Total** | **14** | **10 free, 2 paid, 2 varies** |

## Frontmatter Schema

Every prompt uses YAML frontmatter:

```yaml
---
prompt_id: unique_identifier
version: "1.0.0"
owner: system|l1_nervous|l2_brain|l3_shield|l5_muscle
model_tier: any|local_fast|local_deep|cloud_std|cloud_prem
token_budget: 1024
input_schema: |
  { field: type }
output_schema: |
  { field: type }
eval_cases:
  - input: { ... }
    expected: { ... }
forbidden_inputs: []
source_files: []
status: active|draft|deprecated
---
```

## Related Policies

- `.agents/policies/WORKSPACE_RULES.yaml` — operational boundaries
- `.agents/policies/MODEL_ROUTING_POLICY.yaml` — tier routing rules
- `.agents/policies/MCP_SECURITY_POLICY.yaml` — MCP lifecycle security

## Related Registries

- `.aiwg/registry/prompts_registry.json` — machine-readable registry of all prompts
- `.aiwg/registry/docs_registry.json` — documentation asset registry
- `.aiwg/registry/skills_registry.json` — skill registry
- `.aiwg/registry/mcp_registry.json` — MCP tool registry
