# Contract Audit — DUMMIE Engine

**Fecha:** 2026-04-29  
**Commit:** `973ea40` (main) + truth correction iteration  
**Auditor:** Antigravity automated audit

---

## Contratos Verificados

### 1. `read_spec` (L1 Nervous)

| Campo | Valor Real |
|---|---|
| **Ubicación** | `layers/l1_nervous/tools_impl/core.py` |
| **Parámetro** | `spec_id: str` (NO `spec_path`) |
| **Semántica** | Búsqueda substring en nombres de archivo |
| **Directorio** | `doc/specs/` (con validación de realpath) |
| **Path traversal** | Bloqueado (`..`, `/`, `\`, null byte) |
| **Retorno error** | JSON estructurado con campo `error` |
| **Frontmatter** | YAML parsing opcional si existe `---` |
| **Estado** | ✅ IMPLEMENTED (corregido en T3) |

### 2. `BaseAuditor` Port (L2 Brain)

| Campo | Valor Real |
|---|---|
| **Ubicación** | `layers/l2_brain/auditor_port.py` |
| **Firma** | `async def audit(dag_xml: str, goal: str = "") -> Tuple[bool, str]` |
| **Implementaciones** | `TopologicalAuditor` (L3), `BudgetAuditor` (L3), `ComplianceAuditor` (L3) |
| **Fallback** | `_FallbackUnsafeAuditor` (L2, con warning log) |
| **Estado** | ✅ IMPLEMENTED |

### 3. `TopologicalAuditor` (L3 Shield)

| Campo | Valor Real |
|---|---|
| **Ubicación** | `layers/l3_shield/topological_auditor.py` |
| **Input** | XML string con `<edge source="A" target="B"/>` |
| **Algoritmo** | DFS con recursion stack |
| **Fallback textual** | ❌ ELIMINADO (rechaza non-XML con error) |
| **KuzuDB integration** | Constructor acepta `kuzu_adapter` pero no se usa todavía |
| **Estado** | ✅ IMPLEMENTED (corregido en T4) |

### 4. `NativeShieldAdapter` → `UnsafeBypassShieldAdapter` (L2 Brain)

| Campo | Valor Real |
|---|---|
| **Ubicación** | `layers/l2_brain/adapters.py` |
| **Estado anterior** | `NativeShieldAdapter` con bypass incondicional |
| **Estado actual** | Renombrado a `UnsafeBypassShieldAdapter` |
| **Protección** | Bloqueado por defecto. Requiere `DUMMIE_ALLOW_UNSAFE_BYPASS=true` |
| **Alias** | `NativeShieldAdapter = UnsafeBypassShieldAdapter` (backward compat) |
| **Estado** | ✅ DEPRECATED (corregido en T1) |

### 5. `DummieDaemon` Shield Wiring (L2 Brain)

| Campo | Valor Real |
|---|---|
| **Ubicación** | `layers/l2_brain/daemon.py` |
| **s_shield** | `TopologicalAuditor()` si importación funciona, else `_FallbackUnsafeAuditor()` |
| **e_shield** | `BudgetAuditor()` si importación funciona, else `_FallbackUnsafeAuditor()` |
| **l_shield** | `ComplianceAuditor()` si importación funciona, else `_FallbackUnsafeAuditor()` |
| **Fallback message** | `"FALLBACK_UNSAFE: L3 Shield import failed"` |
| **Estado** | ✅ IMPLEMENTED (corregido en T6) |

### 6. `mcp_server.py` STDIO Purity (L1 Nervous)

| Campo | Valor Real |
|---|---|
| **Ubicación** | `layers/l1_nervous/mcp_server.py` |
| **sys.stdout mutation** | Solo dentro de `if __name__ == "__main__"` block |
| **sys.path hack** | 3 paths (l1, l2, l3) documentados con `TECHNICAL DEBT` |
| **Estado** | ⚠️ PARTIAL (deuda técnica documentada, tests de regresión) |

### 7. `AgentIntent.rationale` (L2 Brain)

| Campo | Valor Real |
|---|---|
| **Ubicación** | `layers/l2_brain/models.py` |
| **`rationale`** | Propiedad `@property` que retorna `self.goal` |
| **Campo canónico** | `goal: str` |
| **Estado** | ✅ IMPLEMENTED (alias legacy) |

### 8. `SixDimensionalContext` (L2 Brain)

| Campo | Valor Real |
|---|---|
| **Ubicación** | `layers/l2_brain/models.py` |
| **Campos canónicos** | `locus_x`, `locus_y`, `locus_z`, `lamport_t`, `authority_a`, `intent_i` |
| **Metadata** | `metadata: Dict[str, Any]` |
| **Estado** | ✅ IMPLEMENTED |

---

## Contratos Pendientes / Parciales

| Contrato | Estado | Motivo |
|---|---|---|
| `TopologyGraphPort` | ❌ NO EXISTE | No se ha creado el puerto para KuzuDB |
| Validación fronteras L0/L1/L2/L3 | ❌ NO EXISTE | El auditor solo valida ciclos, no fronteras de capas |
| `self_optimization.py` autopoiesis | ⚠️ PARTIAL | Solo calcula señal, no cierra loop |
| `sys.path` hacks en L1 | ⚠️ DOCUMENTED | Deuda técnica documentada, no eliminada |
