# Spec 127: Strategic Partner Swarm

## Purpose
Provide a bounded, advisory-only reasoning layer where multiple specialized roles can review mission plans, repository evidence, and coherence results to produce high-confidence recommendations.

## Scope
- Role definition: planner, critic, validator, mentor, risk_officer, execution_advisor.
- Input consumption: roadmap, repo probe, mission artifacts, coherence guards.
- Output: Structured `SwarmDecision` with consensus and dissent.

## Runtime Behavior
1. Gather all latest physical evidence from `.aiwg/reports/`.
2. Instantiate deterministic agents for each role.
3. Each role evaluates the evidence according to its focus (e.g., Critic looks for contradictions).
4. Aggregate individual opinions into a swarm decision.
5. If coherence guard failed, the swarm MUST block or recommend repair.
6. Produce `strategic_partner_swarm_latest.json`.

## Safety Rules
- **Advisory-only**: Swarm cannot execute shell commands or write to non-report files.
- **No direct mutation**: Mutation authority remains with the orchestrator or human.
- **No LLM required**: Initial MVP uses deterministic logic based on report decisions.

## Advisory Policy
The swarm is a cognitive mirror. It reflects the consistency (or lack thereof) of the system's own artifacts.
