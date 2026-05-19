---
spec_id: "165_cognitive_lifecycle_contract"
title: "Cognitive Lifecycle Contract"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "PACK_R3"
layer: "runtime_governance"
created_by: "codex"
created_on: "2026-05-19"
last_verified_on: "2026-05-19"
depends_on:
  - "108_truth_hierarchy"
---

# Spec 165: Cognitive Lifecycle Contract

## Purpose
Define el órgano runtime responsable de enforzar la jerarquía de verdad (Spec 108) antes de aceptar cualquier afirmación arquitectónica o de código como válida. Convierte la disciplina de evidencia en organismo ejecutable que protege la integridad del sistema frente a conjeturas, intuiciones o información obsoleta.

## Responsibilities
1. Cargar AGENTS.md, specs activas y políticas críticas al inicio de cada sesión
2. Aplicar Spec 108 (Truth Hierarchy & Canonicality Policy) antes de aceptar una afirmación como verdad
3. Bloquear respuestas arquitectónicas y mutaciones de código si no hay evidencia suficiente
4. Exigir repo_probe, truth_resolution, tests, o human_review según nivel de riesgo
5. Emitir un EvidenceReceipt obligatorio por acción importante
6. Escribir resultado en .aiwg/reports/cognitive_lifecycle_latest.json
7. Si aplica, cristalizar en memoria 4D-TES (KùzuDB)
8. Proveer contexto común multisesión mediante .aiwg/runtime/session_context.json

## Interface
El órgano debe implementar exactamente esta interfaz:

```python
class CognitiveLifecycleContract:
    @staticmethod
    def load() -> 'CognitiveLifecycleContract':
        """Carga el contrato desde specs activas y políticas críticas"""
        ...
    
    def preflight(self, intent: str, risk: RiskLevel, sources: List[Source]) -> Decision:
        """Evalúa si se puede proceder con la intención dada"""
        ...
    
    def postflight(self, result: Any, verification: VerificationResult, memory_write: bool) -> EvidenceReceipt:
        """Procesa el resultado y genera el recibo de evidencia"""
        ...
```

### Tipos Definidos
```python
enum RiskLevel {
    LOW,          # Cambios triviales, documentación
    MEDIUM,       # Lógica de negocio, configuración
    HIGH,         # Arquitectura, APIs públicas, seguridad
    CRITICAL      # L3 Shield, núcleo de memoria, especificaciones vivas
}

enum Source {
    CODE_TESTS,       # Código + tests pasando
    ACTIVE_SPECS,     # Specs activas + rules.json + feature flags
    MACHINE_SCHEMAS,  # Schemas machine-readable (Kùzu, JSON Schema)
    MEMORY_NODES,     # MemoryNode4D en 4D-TES
    GENERATED_REPORTS,# Reports generados por el sistema
    HUMAN_NOTES       # Memoria humana / chat / notas (menor peso)
}

class Decision {
    blocked: bool
    reason: str
    required_evidence: List[Source]  # Qué fuentes se necesitan para desbloquear
    human_review_required: bool
}

class EvidenceReceipt {
    operation_id: str
    timestamp: ISO8601
    intent: str
    risk_level: RiskLevel
    winning_sources: List[Source]   # Fuentes que ganaron la jerarquía
    losing_sources: List[Source]    # Fuentes que perdieron por peso o antigüedad
    evidence_used: Dict[Source, float]  # Peso contribuido por cada fuente
    verification_passed: bool
    memory_crystallized: bool
    human_review_provided: bool
    next_actions: List[str]
}
```

## Truth Hierarchy Enforcement
El contrato aplica Spec 108 con estos pesos dinámicos (ajustables por riesgo):

| Fuente | Peso Base | Condiciones de Ajuste |
|--------|-----------|------------------------|
| CODE_TESTS | 0.35 | +0.15 si tests de cobertura >90%, -0.2 si tests flakeantes |
| ACTIVE_SPECS | 0.25 | +0.1 si spec revisada en <7d, -0.3 si especificada como DEPRECADA |
| MACHINE_SCHEMAS | 0.15 | +0.1 si schema versionado y backward-compatible |
| MEMORY_NODES | 0.10 | +0.05 si nodo accesado en <24h y con alta relevancia semántica |
| GENERATED_REPORTS | 0.10 | +0.05 si report validado por múltiples agentes |
| HUMAN_NOTES | 0.05 | -0.03 si nota >30d sin validación técnica |

**Umbral de aceptación**: Se requiere mínimo 0.60 peso total para considerar una afirmación "VERIFIED".

## Risk-Based Requirements
Según el nivel de riesgo, se exige:

| Riesgo | Evidencia Mínima Requerida | Acción si Falla |
|--------|----------------------------|-----------------|
| LOW | Una fuente cualquiera de peso >0.10 | Advisory warning |
| MEDIUM | CODE_TESTS + (ACTIVE_SPECS o MACHINE_SCHEMAS) | Bloqueo con sugerencia de prueba |
| HIGH | CODE_TESTS + ACTIVE_SPECS + verificación en staging | Bloqueo requerido, human_review opcional |
| CRITICAL | Todas las fuentes excepto HUMAN_NOTES + human_review explícito | Bloqueo absoluto hasta resolución |

## Entry Points Obligatorios
Todas las siguientes vías DEBEN pasar por el contrato antes de producir output arquitectónico o de código:

1. **Sesiones de código**: Codex, OpenCode, Gemini sessions
2. **Heartbeat**: Daemon y tareas programadas
3. **dummie advise/status**: Interfaz de consulta directa
4. **daemon process_request**: Procesamiento de peticiones externas
5. **MCP tools**: Cualquier herramienta expuesta vía Meta-Gateway
6. **mission queue**: Tareas autónomas de alto nivel
7. **subagent-driven-development**: Trabajo de agentes especializados

## Invariantes Centrales
Estas reglas NUNCA pueden ser violadas:

1. **Nunca se acepta "sé esto"** si la evidencia solo viene de:
   - Chat/memoria informal sin validación técnica
   - Intuición o razonamiento puro sin apoyo en specs/tests
   - Información obsoleta (timestamp > horizonte de relevancia)
   - Fuentes en conflicto sin resolución documentada

2. **Siempre se clasifica la certeza** en exactamente uno de:
   - VERIFIED: código/tests/spec lo respaldan (peso ≥0.60)
   - PROBABLE: evidencia parcial (0.40 ≤ peso < 0.60)
   - STALE: evidencia válida pero antigüedad > horizonte de relevancia
   - CONFLICTED: fuentes se contradicen y requieren resolución
   - UNKNOWN: no investigado (peso < 0.20)
   - REQUIRES_HUMAN: decisión de autoridad humana necesaria (riesgo CRITICAL sin human_review)

3. **El EvidenceReceipt es obligatorio** para:
   - Cualquier mutación de código
   - Decisiones arquitectónicas (cualquier cambio en capas L0/L1/L2)
   - Actualizaciones de specs machine-readable
   - Operaciones de memoria 4D-TES (crystallize/recall)
   - Integración de nuevas capabilities externas

## Multisesión y Multi-Modelo
Cada sesión/modelo recibe un paquete de contexto común:

```json
{
  "session_id": "uuid",
  "bootstrap_time": "ISO8601",
  "contract_version": "semver",
  "active_specs_hash": "sha256",
  "truth_hierarchy_weights": {
    "code_tests": 0.35,
    "active_specs": 0.25,
    "machine_schemas": 0.15,
    "memory_nodes": 0.10,
    "generated_reports": 0.10,
    "human_notes": 0.05
  },
  "risk_thresholds": {
    "low": 0.20,
    "medium": 0.40,
    "high": 0.60,
    "critical": 0.80
  }
}
```

Este contexto se carga desde:
- `.aiwg/runtime/session_context.json` (común para todas las sesiones)
- `.aiwg/reports/cognitive_lifecycle_latest.json` (estado último contrato)
- `.aiwg/reports/self_improvement_action_queue.json` (prioridades actuales)
- `.aiwg/memory/loci.db` (fuente de verdad operacional 4D-TES)

## Ciclo de Operación
```mermaid
flowchart TD
    A[Inicio de Sesión/Evento] --> B[Cargar CognitiveLifecycleContract]
    B --> C[Aplicar Spec 108: Jerarquía de Verdad]
    C --> D[Evalúar Riesgo e Intent]
    D --> E{¿Pasó preflight?}
    E -->|No| F[Bloquear: Devolver NEEDS_EVIDENCE_OR_HUMAN_REVIEW]
    E -->|Sí| G[Ejecutar Acción/Intención]
    G --> H[Recopilar Evidencia y Verificación]
    H --> I[postflight(): Generar EvidenceReceipt]
    I --> J[Escribir en .aiwg/reports/]
    J --> K{¿Crystallize en 4D-TES?}
    K -->|Sí| L[Escribir en MemoryNode4D/Kùzu]
    K -->|No| M[Fin del Ciclo]
    L --> M
```

## Implementación Canónica Recomendada
Fase 1 (Advisory): Contract en modo warning-only, no bloquea
Fase 2 (Arquitectónico): Bloquea solo decisiones de arquitectura y specs
Fase 3 (Extensión): Se aplica a heartbeat/misiones multi-modelo
Fase 4 (Cristalización): Escritura automática en 4D-TES cuando VERIFIED

## Tests de Vida
El contrato debe incluir tests que fallen si:
- Una sesión responde arquitectura sin pasar preflight()
- Se omite generar EvidenceReceipt para mutación de código
- Se ignora un bloqueo de riesgo CRITICAL sin human_review
- La jerarquía de verdad no respeta los pesos definidos
- El contexto común multisesión no se propaga correctamente

## Relación con Otros Componentes
- **Es consumido por**: Meta-Gateway Dynamic Discovery (filtra capabilities externas)
- **Consume**: Spec 108 (jerarquía de verdad), Spec 123 (repo probe determinístico)
- **Produce**: .aiwg/reports/cognitive_lifecycle_latest.json (entrada para heartbeat)
- **Alimenta**: 4D-TES mediante cristalización de nodos verificados
- **Protege**: L3 Shield al asegurar que solo código válido toca especificaciones vivas

## Estado Actual
Esta spec define el órgano que falta para hacer ejecutable Spec 108. Su implementación es requisito previo para:
- PACK R3 (L2 Brain Organ Reorganization sin riesgo de regresión)
- Integración segura de capabilities externas vía Meta-Gateway
- Operación autónoma real con sesiones coordinadas y verdad compartida
- Cumplimiento del Engineering Mandate: evolvability first mediante verdad verificable

## Current State
Spec 165 is the canonical design contract for the runtime governance organ. It is not yet a fully blocking runtime implementation; it currently defines the required interface, evidence receipt schema, entry points, and phased enforcement path.

## Physical Evidence
- `.aiwg/specs/165_cognitive_lifecycle_contract.md`
- `.aiwg/specs/165_cognitive_lifecycle_contract.feature`
- `.aiwg/specs/165_cognitive_lifecycle_contract.rules.json`
- `.aiwg/schemas/cognitive_lifecycle_receipt.schema.json`

## Contract Invariants
- Architectural or code claims must be classified against the truth hierarchy before acceptance.
- High-risk and critical actions must require evidence receipts.
- Human notes and chat memory must never outrank code, tests, active specs, or machine schemas.
- Multi-session agents must share a common lifecycle context before mutating canonical files.
- Runtime implementation must start advisory and progress to blocking only with tests and receipts.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check .aiwg/specs/165_cognitive_lifecycle_contract.md
python3 -m json.tool .aiwg/specs/165_cognitive_lifecycle_contract.rules.json
python3 -m json.tool .aiwg/schemas/cognitive_lifecycle_receipt.schema.json
```

## Traceability
| Relationship | Artifact | Role |
| --- | --- | --- |
| rules | `.aiwg/specs/165_cognitive_lifecycle_contract.rules.json` | Machine-readable lifecycle enforcement rules |
| schema | `.aiwg/schemas/cognitive_lifecycle_receipt.schema.json` | EvidenceReceipt validation schema |
| feature | `.aiwg/specs/165_cognitive_lifecycle_contract.feature` | BDD acceptance behavior |

---
*Spec escrita en cumplimiento del rol de socio estratégico: propone estructura canónica, espera aprobación soberana antes de implementación.*
