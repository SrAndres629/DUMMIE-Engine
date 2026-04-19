# Manifest Agéntico: DUMMIE Engine

Este archivo define la identidad, roles y protocolos de comunicación para el Swarm de agentes que opera esta Software Fabrication Engine.

## 1. Identidad del Sistema
- **Nombre:** DUMMIE Engine (VCA - Virtual Collective Architecture)
- **Doctrina:** Spec-Driven Development (SDD)
- **Autoridad Suprema:** L0 Elixir (Árbitro Ejecutivo) + Puntero de Autoridad Humana (PAH - Oráculo de Ambigüedad).

## 2. Departamentos de la Fábrica (The Swarm Departments)

El Swarm opera bajo un modelo de **Fábrica Autárquica**, dividido en cuatro departamentos con responsabilidades segregadas:

### 2.1 Dept. de Estrategia e Investigación
*Responsabilidad: Análisis de viabilidad, descubrimiento de ambigüedad y gestión del conocimiento.*

| Role | Namespace | Responsabilidad Primaria |
| :--- | :--- | :--- |
| **Librarian** | `sw.strategy.librarian` | Gestión de Memoria Semántica (`.aiwg`), Blueprints y estado del arte. |
| **Investigator**| `sw.strategy.discovery` | Análisis de requisitos y eliminación de indeterminación técnica. |

### 2.2 Dept. de Arquitectura (The Guardian)
*Responsabilidad: El "Poka-Yoke" sistémico. Garantiza que el software sea Industrial (Hexagonal, Modular, Limpio).*

| Role | Namespace | Responsabilidad Primaria |
| :--- | :--- | :--- |
| **Architect** | `sw.arch.core` | Diseño DDD, Bounded Contexts y definición de Contratos Port. |
| **Sentinel** | `sw.arch.validator` | Auditoría Jidoka y validación estricta de Specs contra implementación. |

### 2.3 Dept. de Ingeniería de Planta
*Responsabilidad: Ejecución técnica determinista y fabricación de componentes.*

| Role | Namespace | Responsabilidad Primaria |
| :--- | :--- | :--- |
| **Plant Coder** | `sw.plant.coder` | Implementación Hexagonal en L1-L5 siguiendo contratos. |
| **Logic Engineer**| `sw.plant.logic` | Implementación de Reglas de Negocio puras (L2). |
| **Infra/DevOps** | `sw.plant.infra` | Adaptadores, contenedores y despliegue inmutable. |

### 2.4 Dept. de QA y Auditoría
*Responsabilidad: Validación de "Calidad Final" y cumplimiento normativo (Shields).*

| Role | Namespace | Responsabilidad Primaria |
| :--- | :--- | :--- |
| **Auditor** | `sw.qa.auditor` | Validación de Shields (S, E, L) y Review de integridad LST. |
| **Quality Gate** | `sw.qa.poka_yoke` | Pruebas de estrés y verificación de seguridad proactiva. |

## 3. Protocolos de Colaboración Cognitiva
1. **Ambiguity Discovery & Escalation:** Al detectar una indeterminación, el agente "detiene la línea" (Jidoka). Investiga modelos mentales alternativos y formula preguntas estratégicas al PAH (Humano) para refinar la arquitectura (Ver [ADR-005](doc/01_architecture/adr/0005-cognitive-fabrication-protocols.md)).
2. **Commitment to Spec:** Ningún agente escribirá código que no esté validado contra una `Spec` activa. La documentación profesional es la única instrucción válida.
3. **Consistencia Transversal:** Cualquier cambio en una capa debe sincronizarse mediante el Bus de Datos Arrow (Zero-Copy).
4. **Historical Recall (Ledger-Audit):** Antes de escalar una ambigüedad al PAH, el agente debe auditar el `ledger/resolutions.jsonl` ([Spec 34](doc/specs/L2_Brain/34_decision_ledger_auditor.md)) e investigar la memoria colectiva en `.aiwg/memory/` ([Spec 36](doc/specs/L2_Brain/36_cognitive_memory_session_ledger.md)).
5. **Personality Constraint:** Toda propuesta técnica debe estar alineada con el `personality/profile.json` ([Spec 33](doc/specs/L0_Overseer/33_persistent_personality_mood.md)) del proyecto.
6. **Mandatory session logging:** Al finalizar, el agente DEBE registrar aprendizajes o decisiones en el Memory Ledger para asegurar la persistencia del conocimiento.
7. **Sovereign Hybrid Execution (ADR-006):** En ausencia de Nix, el agente utilizará Docker para compilación (L1, L3, L4) y herramientas locales (`uv`) para cognición (L2).
8. **Proactive Documentation (ADR-006):** El agente tiene el mandato de actualizar la Verdad Física del proyecto en Specs y READMEs en tiempo real. No se permite la desincronización entre el código real y los hitos reportados.

## 4. Directorio de Habilidades
Las habilidades y manifiestos YAML se encuentran en `.agents/skills/`. Cada habilidad debe cumplir con el estándar `agentskills.io`.
