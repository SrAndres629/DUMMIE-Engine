# 📝 Plan de Implementación Industrial: L2_BRAIN Alignment (V2.2)

> **Objetivo:** Alcanzar paridad 1:1 con las especificaciones del Bounded Context L2_Brain y cerrar la brecha del puente de infraestructura KùzuDB.

## 🚀 Fase 1: Alineación de Cimientos (Domain & App) - **PRIORIDAD ALTA**
Asegurar que toda la capa de aplicación hable el lenguaje de la Spec 12 (6D-Context).

- [ ] **Tarea 1.1:** Refactorizar `application/use_cases/orchestrator.py` para eliminar `Vector6D` y adoptar `SixDimensionalContext`.
- [ ] **Tarea 1.2:** Unificar `IntentType` en `domain/context/models.py` y `domain/fabrication/models.py`. (Solemne: La intención es un vector de 6D).
- [ ] **Tarea 1.3:** Implementar `BrainInputPort` y `ShieldOutputPort` con firmas tipadas estrictas en `application/ports.py`.

## 🧠 Fase 2: Puente de Memoria Loci (Infrastructure) - **PRIORIDAD CRÍTICA**
Ejecutar el ADR-0011 para permitir la persistencia causal.

- [ ] **Tarea 2.1:** Crear `infrastructure/adapters/kuzu_repository.py`.
- [ ] **Tarea 2.2:** Implementar el esquema de nodos (`Event`, `Agent`, `Requirement`) y relaciones en KùzuDB conforme a la Spec 02.
- [ ] **Tarea 2.3:** Implementar el `4D-TES Causal Hash` (SHA-256) en la lógica de persistencia.

## ⚖️ Fase 3: Gobernanza y Ledger (Integrity)
Materializar la trazabilidad de la soberanía cognitiva.

- [ ] **Tarea 3.1:** Implementar el registro automático de decisiones en `.aiwg/memory/decisions.jsonl` desde el Orquestador.
- [ ] **Tarea 3.2:** Integrar el cálculo del `Witness Hash` (Spec 34) en el flujo de auditoría.

## ⚙️ Fase 4: Logic Engine (Fabrication)
Activar el corazón de la SFE.

- [ ] **Tarea 4.1:** Implementar la lógica del `KaizenLoop` en `orchestrator.py`.
- [ ] **Tarea 4.2:** Orquestar la validación Spec-First antes de la ejecución física.

---

## 🛡️ Invariantes de Calidad
1. **Poka-Yoke:** Ninguna mutación sin `CausalHash` válido.
2. **Jidoka:** Si KùzuDB falla, la sesión se aborta inmediatamente.
3. **SDD Compliance:** Los tests de `tests/l2_brain` deben validar el esquema de 6 dimensiones.
