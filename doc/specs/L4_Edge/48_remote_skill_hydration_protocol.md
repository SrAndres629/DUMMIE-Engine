---
spec_id: "DE-V2-L4-48"
title: "Protocolo de Hidratación Remota de Habilidades (Agentic Skill Fetcher)"
status: "ACTIVE"
version: "1.0.0"
layer: "L4"
namespace: "io.dummie.v2.edge.hydration"
authority: "SENTINEL"
dependencies:
  - id: "DE-V2-L2-28"
    relationship: "INSTALLS_CONTRACT"
  - id: "DE-V2-L3-04"
    relationship: "AUDITED_BY"
tags: ["edge_layer", "skill_hydration", "remote_fetching", "marketplace_parity", "claw_ism"]
---

# 48. Protocolo de Hidratación Remota de Habilidades (Agentic Skill Fetcher)

## Abstract
Inspirado por la capacidad de **OpenClaw (ClawHub)** de descargar e instalar habilidades dinámicamente, esta especificación dota al sistema de una frontera de adquisición de conocimiento global. El sistema permite a los agentes solicitar el andamiaje de nuevas capacidades desde repositorios externos (GitHub, GitLab, etc.), procesándolas a través de un riguroso pipeline de auditoría de seguridad en Layer 3 antes de su integración física en el monorepo.

## 1. La Frontera de Adquisición
La Hidratación Remota dota al sistema de una frontera de adquisición de conocimiento global. El sistema permite a los agentes solicitar el andamiaje de nuevas capacidades desde repositorios externos, integrándolas de forma segura tras una auditoría exhaustiva.

- **Fuentes**: Soporte para protocolos Git (HTTPS) con lista blanca de dominios autorizados (ej. GitHub).
- **Pipeline de Auditoría**: Descarga en zona estéril -> Validación SDD -> Análisis Estático de Malware/Hooks -> Aprobación PAH.
- **Despliegue**: Instalación atómica en el monorepo y registro en la memoria semántica (LST).

Para los detalles técnicos de los protocolos de descarga y los invariantes del pipeline de auditoría, consulte el archivo de reglas [48_remote_skill_hydration_protocol.rules.json](48_remote_skill_hydration_protocol.rules.json).

---

## 2. El Proceso de Hidratación (L4 Edge Gateway)
El agente L2 dispara la hidratación mediante un `Intent` de adquisición:

1.  **Request:** El Cerebro emite un comando: `ao.v2.edge.fetch_skill(url="https://github.com/user/skill_name")`.
2.  **Edge Fetch:** El componente Layer 4 realiza la descarga en un entorno aislado (`tmp/sterile/`).
3.  **Security Gate:** El Escudo L3 (Sentinel) escanea el `SKILL.md` y los scripts asociados buscando patrones de infiltración o exfiltración.
4.  **Crystallization:** Si pasa la auditoría (y el PAH no veta), la Skill se mueve a la carpeta de producción y se registra en la memoria semántica.

---

## 3. Invariantes de Soberanía
- **No-Auto-Exec:** Ninguna Skill remota puede ejecutarse inmediatamente tras la descarga si no existe un archivo `.rules.json` válido y auditado.
- **Hash Verification:** Si el registro proporciona un hash, el sistema debe verificar la integridad del andamiaje antes de la hidratación.

---

## [MSA] Sibling Components
- **Executable Contract**: [48_remote_skill_hydration_protocol.feature](48_remote_skill_hydration_protocol.feature)
- **Machine Rules**: [48_remote_skill_hydration_protocol.rules.json](48_remote_skill_hydration_protocol.rules.json)
