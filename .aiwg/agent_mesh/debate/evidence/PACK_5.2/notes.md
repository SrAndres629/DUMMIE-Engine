# PACK_5.2: Migrar o DEPRECATED los 30 módulos flat_brain con spec

## What was done
1. **36 modules marked DEPRECATED** — flat_brain modules referenced by specs
   with no canonical counterpart. Each got `# DEPRECATED: ...` header.
   These will be removed in PACK_5.5.

2. **Spec .md files updated** — 9 spec files had flat_brain paths replaced
   with canonical equivalents (memory/, metacognition/, model_mesh/, daemon/).
   4 spec files had references to truly-deleted modules removed.

3. **Spec registry** — 88 specs, 0 errors (down from 13).

## Pre-existing issues (not caused by PACK_5.2)
- 1 test fails: `test_flat_brain_fallback_does_not_delete_existing_kuzu_file`
  (flat_brain_LEGACY import chain broken, unrelated)
- ollama_runtime + model_executor pre-existing critical_failures

## Result
- Import chain: OK (both dummie.engine and layers.l2_brain)
- Tests: 3/4 pass, 1 pre-existing failure
- Spec registry: 88 specs, 0 errors
