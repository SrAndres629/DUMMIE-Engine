# AIWG Governance Kernel Freeze Audit (v0.4)

Generated at: 2026-05-19T04:25:00Z  
HEAD Commit: `679d57d10702714019745f2775152cba70f142f8`  
Decision: **KERNEL_FROZEN**  

---

## 🛠️ Comandos Disponibles

The AIWG Pack Governance CLI is fully frozen with the following subcommands:
* **`preflight`**: Verifies active pack preconditions, checks freshness gates, and checks for anti-overclaim terms.
* **`self-critique`**: Collects and validates self-critique answers, ensuring no optimistic placeholders or unverified defaults are present.
* **`run-required`**: Runs required commands and tests autonomously, capturing stdout/stderr into validation logs.
* **`closeout`**: Concludes the active pack, validates that the runner-generated evidence matches HEAD, logs history, and transitions the project state to the next milestone.
* **`distance`**: Evaluates remaining steps and high-leverage pack paths towards the ultimate Pack 6.1 goal.
* **`next-pack`**: Schedules the next legally permitted pack, strictly enforcing transition skip prevention rules.

---

## 📊 Schema Estable

The governance kernel API defines stable schemas across all `.aiwg` interfaces:
1. **`current_truth.json`**: Anchors project branch, Git commit context, active capability matrices, and references to active reports.
2. **`active_pack.json`**: Explicitly defines the execution contract, rollback steps, stop conditions, and test commands.
3. **`pack_roadmap_to_6_1.json`**: Tracks the sequential order of completion, preconditions, and dependencies for all packs.
4. **`pack_validation_evidence_latest.json`**: The canonical proof of execution runner ledger capturing precise logs, durations, and environment.

---

## 🚫 Qué Queda Fuera

* **Automatic Git Commits/Tags**: Closeout does not automatically write commits to avoid conflicting with the agent's worktree policies or host credentials.
* **Real-time Cost Interception**: Guard execution is light; budget metering is delegated to `ContextBudgetManager`.

---

## 🚀 Triggers para Versión 0.5

The following future architectural updates will require stepping the kernel version to `0.5`:
* Adding support for parallel/multi-branch pack developments.
* Integrating direct webhooks or reporting gateways to remote telemetry servers.

---

> [!IMPORTANT]
> **CONSOLIDATED DECISION: KERNEL_FROZEN**  
> All pre-pack checks, reranker suites, embedding contracts, and spec validations are passing with 100% compliance. Socraticode workflows are locked. Siguiente pack permitido: **PACK_3.2**.
