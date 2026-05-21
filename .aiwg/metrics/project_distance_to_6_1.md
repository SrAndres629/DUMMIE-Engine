# Project Distance to 6.1 — DUMMIE Engine

This tracks progress towards the long-term target of Pack 6.1 (Golden Path E2E).

---

## Component Completion Scores (0.0 to 1.0)

| Component | Completion Score | Remaining Distance | Verification State |
| :--- | :--- | :--- | :--- |
| **Structural Debt** | `0.85` | `0.15` | `verified` |
| **Semantic Capability** | `0.55` | `0.45` | `estimated` |
| **Model Mesh** | `0.20` | `0.80` | `unverified` |
| **Guardrails** | `0.10` | `0.90` | `unverified` |
| **Function Calling** | `0.15` | `0.85` | `unverified` |
| **Local Runtime** | `0.25` | `0.75` | `unverified` |
| **Golden Path** | `0.05` | `0.95` | `unverified` |

---

* **Current Score**: `0.37` (`estimated`)
* **Blockers**:
  * Falta de indexación de código AST.
  * Falta de router de capacidades de modelos.
  * Falta de Golden Path E2E.
* **Next Highest Leverage Pack**: `PACK_3.2`
* **Why this Pack Next**: El indexador AST de código separará la estructura de sintaxis del corpus de texto genérico, lo que se estima que aumentará la precisión y la relevancia de las consultas sintácticas cuando sea medido formalmente.
* **What NOT to do Next**: No saltarse a Pack 4.x antes de cerrar la separación del espacio vectorial de código.
* **Nota**: El Pack 6.1 (Golden Path E2E) sigue lejos del alcance actual dado que la persistencia relacional e inferencia causal no han sido demostradas en un flujo integrado de extremo a extremo sin intervenciones.
