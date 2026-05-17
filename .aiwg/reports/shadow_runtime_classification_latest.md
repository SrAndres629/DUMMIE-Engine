# DUMMIE Shadow Runtime Classification Report

**Classification ID:** `cla-d509a590`
**Timestamp:** 2026-05-17T00:53:49.224528+00:00

## Shadow Audit Status: **PASS_WITH_WARNINGS**

### Shadow Modules Summary
- **Total Shadow Modules Audited:** `152`

### Non-Destructive Classifications
| Module Path | Classification | Confidence | Recommended Action |
|---|---|---|---|
| [local_ssh_context_sdk.py](file:////media/datasets/DUMMIE Engine/layers/l1_nervous/legacy/local_ssh_context_sdk.py) | `legacy_candidate` | `90.0%` | **archive** |
| [build_inventory.py](file:////media/datasets/DUMMIE Engine/scripts/build_inventory.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [build_repo_maps.py](file:////media/datasets/DUMMIE Engine/scripts/build_repo_maps.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [consciousness_audit.py](file:////media/datasets/DUMMIE Engine/scripts/consciousness_audit.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [context_oracle.py](file:////media/datasets/DUMMIE Engine/scripts/context_oracle.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [dummie_orchestrator.py](file:////media/datasets/DUMMIE Engine/scripts/dummie_orchestrator.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [dummie_repair.py](file:////media/datasets/DUMMIE Engine/scripts/dummie_repair.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [dummie_status.py](file:////media/datasets/DUMMIE Engine/scripts/dummie_status.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [dummie_truth.py](file:////media/datasets/DUMMIE Engine/scripts/dummie_truth.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [harden_specs_docs.py](file:////media/datasets/DUMMIE Engine/scripts/harden_specs_docs.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [industrial_audit.py](file:////media/datasets/DUMMIE Engine/scripts/industrial_audit.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [inject_personality_links.py](file:////media/datasets/DUMMIE Engine/scripts/inject_personality_links.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [orbit_lite_runner.py](file:////media/datasets/DUMMIE Engine/scripts/orbit_lite_runner.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [sync_links.py](file:////media/datasets/DUMMIE Engine/scripts/sync_links.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [validate_specs_docs.py](file:////media/datasets/DUMMIE Engine/scripts/validate_specs_docs.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [verify_compression.py](file:////media/datasets/DUMMIE Engine/scripts/verify_compression.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [verify_swarm_intelligence.py](file:////media/datasets/DUMMIE Engine/scripts/verify_swarm_intelligence.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [watch_repo_events.py](file:////media/datasets/DUMMIE Engine/scripts/watch_repo_events.py) | `script_entrypoint` | `90.0%` | **ignore** |
| [__init__.py](file:////media/datasets/DUMMIE Engine/layers/__init__.py) | `orphan_candidate` | `75.0%` | **wire** |
| [supervisor.py](file:////media/datasets/DUMMIE Engine/layers/l0_overseer/supervisor.py) | `orphan_candidate` | `75.0%` | **wire** |

*Showed top 20 of 152 shadow modules. See JSON report for the full list.*

### Active Warnings
- [WARNING] High volume of shadow modules detected. Recommend priority audit.