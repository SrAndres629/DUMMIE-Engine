---
spec_id: "DE-V2-L4-48"
title: "Protocolo de Hidratación Remota de Habilidades (Agentic Skill Fetcher)"
status: "ACTIVE"
version: "2.2.0"
layer: "L4"
namespace: "io.dummie.v2.edge.hydration"
authority: "SENTINEL"
dependencies:
  - id: "DE-V2-L2-28"
    relationship: "INSTALLS_CONTRACT"
  - id: "DE-V2-L3-04"
    relationship: "AUDITED_BY"
tags: ["edge_layer", "skill_hydration", "remote_fetching"]
---

# 48. Protocolo de Hidratación Remota de Habilidades (Agentic Skill Fetcher)

## Abstract
La **Hidratación Remota** dota al sistema de una frontera de adquisición de conocimiento global. Este componente permite que los agentes soliciten el andamiaje (Scaffolding) de nuevas capacidades desde repositorios externos, procesándolas a través de un pipeline de auditoría en Layer 3 antes de su integración física en el monorepo.

## 1. Cognitive Context Model (Ref)
Para los protocolos soportados (HTTPS Git), la lista blanca de dominios autorizados y los pasos del pipeline de auditoría (Sterile Download, SDD Validation, etc.), consulte el archivo hermano [48_remote_skill_hydration_protocol.rules.json](./48_remote_skill_hydration_protocol.rules.json).

---

## 2. El Proceso de Hidratación (Edge Gateway)
El agente L2 dispara la hidratación mediante un `Intent` de adquisición:
1.  **Request:** Solicitud formal de una nueva capacidad externa.
2.  **Sterile Download:** Descarga en un entorno aislado y efímero en Layer 4.
3.  **Security Gate:** El Escudo L3 (Sentinel) escanea los archivos buscando patrones de infiltración o exfiltración.
4.  **Integration:** Si pasa la auditoría, la Skill se mueve a producción y se indexa en el Palacio de Loci ([Spec 18](18_loci_ontology_mapping.md)).

---

## 3. Invariantes de Soberanía
- **No Auto-Exec:** Ninguna Skill remota puede ejecutarse inmediatamente tras la descarga sin un contrato SDD auditado y firmado.
- **Hash Integrity:** Si el registro proporciona un hash, el sistema debe verificar la integridad absoluta del andamiaje antes de permitir la hidratación.
- **Source Pinning:** Solo se permite la hidratación desde fuentes explícitamente autorizadas en la lista blanca de gobernanza.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [48_remote_skill_hydration_protocol.feature](./48_remote_skill_hydration_protocol.feature)
- **Machine Rules:** [48_remote_skill_hydration_protocol.rules.json](./48_remote_skill_hydration_protocol.rules.json)
