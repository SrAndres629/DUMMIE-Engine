# Spec 128: Debate & Adversarial Review Runtime

## Purpose
Prevent consensus bias and identify planning flaws by forcing a structured debate between specialized roles before any mission execution.

## Scope
- Roles: proposer, skeptic, evidence_auditor, risk_challenger, implementation_reviewer, mentor_judge.
- Detection: missing evidence, coherence failures, consensus bias, unsafe autonomy requests.

## Runtime Behavior
1. Gather reports from previous phases (Repo Probe, Mission Plan, Swarm, Coherence).
2. Execute deterministic adversarial reasoning for each role.
3. Proposer claims readiness; Skeptic challenges with consensus bias checks.
4. Auditor verifies physical evidence grounding.
5. Reviewer checks SDD/TDD compliance (e.g., missing test paths).
6. Mentor Judge issues a final verdict (accept|repair|block).

## Safety Rules
- Advisory-only: no workspace mutation.
- Must block if MissionCoherenceGuard failed.
- Must flag if a plan for a runtime module has no tests.

## Relationship to P26
Consumes StrategicPartnerSwarm outputs to challenge their consensus.
