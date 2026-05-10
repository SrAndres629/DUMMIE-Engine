# Mission Protocol

## Purpose
Convert user prompts into bounded, auditable long-running missions.

## Agent
ColdPlanner, EpistemicJudge, Architect, Builder, Validator, Integrator, and MemoryCurator.

## Format
Mission records include goal, constraints, forbidden actions, phases, required artifacts, validation plan, memory plan, and next loop.

## Allowed
- Plan-only self-worktree sessions.
- Evidence-first validation.
- Patch plans with explicit allowed and forbidden paths.

## Prohibited
- Automatic patch application from mission compilation.
- Destructive shell commands.
- Editing `.env`, `.git`, lockfiles, generated artifacts, or dynamic memory as product code.

## Validation
Compile mission, create artifacts, run tests, then record validation before memory commit.

## 4D-TES / 6D Connection
Mission events are ordered by Lamport time and tied to authority and intent.
