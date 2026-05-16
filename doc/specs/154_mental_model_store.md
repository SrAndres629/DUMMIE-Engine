# Spec 154: Mental Model Store
Purpose: Append-only persistent storage for mental models.
Scope: L2 Brain Metacognition

## Runtime Behavior
Ensures idempotency and rejection of non-compliant models.

## Quality Gate
- FAIL if secrets/private Reasoning detected.
- PASS_WITH_WARNINGS if evidence weak.

## Integration
- Context Gate
- Memory Spine
- Ontology Graph
- Cognitive Frame
