# Research Tree Protocol

## Purpose
Structure investigation before implementation so decisions remain auditable.

## Agent
Architect and EpistemicJudge maintain research trees; Builder consumes only validated branches.

## Format
Markdown artifact `research_tree.md` with goals, evidence, open questions, rejected paths, and validation commands.

## Allowed
- Non-mutating repo inspection.
- Static analysis and dry-run commands.
- Explicit assumptions marked as assumptions.

## Prohibited
- Hidden or private chain-of-thought artifacts.
- Guessing repo facts that can be inspected.

## Validation
Every accepted branch must cite file paths, command output, or test evidence.

## 4D-TES / 6D Connection
Research branches become session artifacts linked from events.
