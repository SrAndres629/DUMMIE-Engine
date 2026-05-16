# Mentor Review Protocol

The mentor or reviewer evaluates each phase report as one of:

- improved;
- neutral;
- regressed.

The review must inspect:

- claims;
- evidence;
- tests;
- restart validation;
- hot-path validation;
- snowball score;
- engine-native reuse;
- risks;
- next phase seed.

The reviewer may require a strategic objection when the phase report contradicts repo evidence, duplicates native engine capability, or claims PASS without verifiable evidence.

## Objection-Focused Delta Audit Policy

External read-only audits, especially Gemini CLI audits, must avoid repeating the full Codex report unless explicitly requested.

The default audit mode is now `objection_focused_delta_audit`.

A read-only auditor should prioritize:

- contradictions between report and repo state;
- missing expected files;
- invalid JSON/YAML;
- failed or missing tests;
- runtime modifications outside scope;
- roadmap drift;
- unregistered debt;
- inflated PASS claims;
- token-expensive recap with no actionable delta.

A good audit should answer:

1. What is wrong?
2. What is missing?
3. What is risky?
4. What changed outside scope?
5. What should block commit or next phase?

If there are no blockers, the audit should be compact and say so.
