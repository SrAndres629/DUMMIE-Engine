# Memory Protocol

## Purpose
Define how DUMMIE stores operational memory without mixing versioned protocols with local runtime state.

## Agent
MemoryCurator owns memory hygiene; Validator checks evidence before memory commit.

## Format
Runtime memory uses JSONL, JSON, Markdown artifacts, and local databases under ignored `.aiwg/` paths.

## Allowed
- Write session artifacts under `.aiwg/sessions/`.
- Write index artifacts under `.aiwg/index/`.
- Preserve old dynamic memory through `.aiwg/runtime/quarantine/`.

## Prohibited
- Commit dynamic memory, local databases, caches, or generated events.
- Treat generated memory as higher authority than tests or source code.

## Validation
Run `git check-ignore -v` for dynamic paths and verify `.aiwg/control/**` remains versionable.

## 4D-TES / 6D Connection
Memory events must include evidence references and 6D context when available.
