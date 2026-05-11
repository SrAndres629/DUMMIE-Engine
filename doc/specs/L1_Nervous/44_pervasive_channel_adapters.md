---
spec_id: "DE-V2-L1-44"
title: "Adaptadores de Canal Pervasivos (The Pervasive Gateway)"
status: "ACTIVE"
version: "2.2.0"
layer: "L1"
namespace: "io.dummie.v2.nervous.adapters"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L1-41"
    relationship: "USES_WIRE"
  - id: "DE-V2-L0-05"
    relationship: "ORCHESTRATED_BY"
tags: ["nervous_system", "channel_adapters", "pervasive_gateway", "claw_ism"]
---

# 44. Adaptadores de Canal Pervasivos (The Pervasive Gateway)

## Abstract
DUMMIE Engine dota al sistema de una presencia ubicua a través de adaptadores para plataformas de mensajería (WhatsApp, Telegram, Slack). El objetivo es que la Software Fabrication Engine (SFE) sea accesible y controlable desde cualquier dispositivo comercial, manteniendo la soberanía y el contexto de sesión.

## 1. Cognitive Context Model (Ref)
Para los canales soportados, los límites de tasa (Rate Limit) y los invariantes de normalización de mensajes (Webhook/Poll -> Intent), consulte el archivo hermano [44_pervasive_channel_adapters.rules.json](./44_pervasive_channel_adapters.rules.json).

---

## 2. El Adaptador de Canal (L1 Bridge)
Cada canal se implementa como un Adaptador en Layer 1 que realiza el mapeo semántico:
1.  **Normalización:** Conversión del payload nativo (JSON) en un mensaje `Intent` de Protobuf.
2.  **Context Injection:** Inyección de metadatos de canal (`channel_id`, `user_handle`) para el Cerebro L2.
3.  **Media Handling:** Procesamiento de imágenes o audios como referencias de `MemoryTicket` para el Palacio de Loci ([Spec 18](../L4_Edge/18_loci_ontology_mapping.md)).

---

## 3. Seguridad y Privacidad
- **Identity Pinning:** El sistema solo responde a identidades (teléfonos, handles) registrados en la lista de autoridad del PAH.
- **End-to-End Governance:** Anonimización o cifrado de contenido sensible antes de salir del enclave L3 (Shield) hacia servidores externos.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [44_pervasive_channel_adapters.feature](./44_pervasive_channel_adapters.feature)
- **Machine Rules:** [44_pervasive_channel_adapters.rules.json](./44_pervasive_channel_adapters.rules.json)
