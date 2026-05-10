# Documentation and Specs Hardening Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalizar documentación y specs para que reflejen el estado real del código y sean verificables de forma automática.

**Architecture:** Se aplica una estrategia en dos capas: correcciones directas de contenido (fuentes de verdad) y un validador automatizado que evita regresiones. Las specs se normalizan con un formato operativo mínimo que conecta contrato, evidencia física y verificación ejecutable.

**Tech Stack:** Markdown, Python 3, regex/path validation, Makefile.

---

### Task 1: Correcciones inmediatas de narrativa desactualizada

**Files:**
- Modify: `README.md`
- Modify: `layers/l2_brain/README.md`
- Modify: `doc/PHYSICAL_MAP.md`
- Modify: `doc/guides/mcp_server_usage.md`

- [ ] Actualizar referencias legacy ya resueltas y comandos de verificación actuales.
- [ ] Corregir referencias de specs inexistentes en guía MCP.

### Task 2: Normalización de estado de spec fuera de contrato

**Files:**
- Modify: `doc/specs/26_langgraph_quantum_swarm.md`
- Modify: `doc/CORE_SPEC.md`

- [ ] Alinear `status` de la spec al set permitido por política.
- [ ] Asegurar consistencia con la clasificación en CORE_SPEC.

### Task 3: Depuración masiva de boilerplate y trazabilidad

**Files:**
- Modify: `doc/specs/*.md` (bulk, controlado)
- Create: `scripts/harden_specs_docs.py`

- [ ] Reemplazar contenido plantilla por estructura operativa mínima.
- [ ] Inyectar invariantes, evidencia física y comandos de verificación por spec.

### Task 4: Validación permanente

**Files:**
- Create: `scripts/validate_specs_docs.py`
- Modify: `Makefile`

- [ ] Implementar chequeos automáticos (estados, boilerplate, evidencia, referencias de spec).
- [ ] Exponer target de mantenimiento para CI/local.

### Task 5: Evidencia de cierre

**Files:**
- Modify: `README.md` (si aplica)

- [ ] Ejecutar validador y pruebas documentales.
- [ ] Reportar resultados y deuda residual concreta.
