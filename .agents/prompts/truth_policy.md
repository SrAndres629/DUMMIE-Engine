---
prompt_id: truth_policy
version: "1.0.0"
owner: system
model_tier: any
token_budget: 600
input_schema: none
output_schema: none
eval_cases: []
legacy_sources:
  - doc/CORE_SPEC.md (Política de verdad, lines 6-9)
  - doc/PHYSICAL_MAP.md (Estado físico actual verificado)
  - .aiwg/reports/language_reality_audit.md (example of unverified claims)
forbidden_inputs: []
status: active
---

# Truth Policy

This prompt defines how agents verify claims before acting on them.

## Core Principle

**Never assert something exists, works, or is implemented without physical evidence.**

The Elixir case: GitHub reported Elixir at ~42% of the codebase. Physical audit revealed 3 first-party files behind 58 vendored dependencies. Claims without verification lead to wrong architecture decisions.

## Sources of Truth

| Document | Authority | Content |
|:---|:---|:---|
| `doc/CORE_SPEC.md` | Index Master | Active specs, their states, their paths |
| `doc/PHYSICAL_MAP.md` | Physical Map | What is actually implemented per layer |
| `.aiwg/registry/*.json` | Registries | Canonical maps of docs, skills, prompts, MCP |
| `.aiwg/reports/*.md` | Audit Reports | Evidence-based findings |

## Verification Rules

### Before claiming something "exists"

```bash
ls -la <path>           # File exists physically
wc -l <path>            # File has non-trivial content
head -20 <path>         # Content matches expectations
```

### Before claiming something "works"

```bash
python3 -m pytest <test_file>    # Tests pass
python3 <script> --help          # Script is runnable
python3 -c "import <module>"     # Module is importable
```

### Before claiming something "is implemented"

```bash
grep -r "def <function_name>" layers/   # Function exists
grep -r "class <ClassName>" layers/     # Class exists
python3 -c "from <module> import <name>; print(type(<name>))"  # It's importable
```

### Before claiming a count or statistic

```bash
find <path> -name "*.py" ! -path "*/deps/*" ! -path "*/.venv/*" | wc -l  # Exclude vendored
```

## Prohibited Assumptions

- "This module probably does X" → Read it first.
- "There are about N files" → Count them.
- "The test should pass" → Run it.
- "This is the same as the other one" → Diff them.
- "It was working before" → Check git log.

## States

From `doc/CORE_SPEC.md`:

| State | Meaning |
|:---|:---|
| `ACTIVE` | Backed by physical evidence in the repo |
| `DRAFT` | Partial design or in transition |
| `PROPOSED` | Hypothesis/roadmap, no implementation |
| `DEPRECATED` | Historical reference, outside active architecture |
