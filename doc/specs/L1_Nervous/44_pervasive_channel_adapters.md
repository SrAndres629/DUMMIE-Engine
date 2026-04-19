---
spec_id: "DE-V2-L1-44"
title: "Adaptadores de Canal Pervasivos (The Pervasive Gateway)"
status: "ACTIVE"
version: "1.0.0"
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
Inspirado por el **Gateway de OpenClaw**, esta especificación dota al sistema de una presencia ubicua a través de adaptadores para plataformas de mensjería (WhatsApp, Telegram, Slack). El objetivo es que la Software Fabrication Engine (SFE) sea accesible y controlable desde cualquier dispositivo comercial, manteniendo la soberanía y el contexto de sesión.


## 1. Definición del Gateway
El Pervasive Gateway actúa como el sistema sensorial externo de la SFE. Su función es normalizar las diversas señales de comunicación (mensajería instantánea) en el lenguaje unificado del sistema nervioso (Protobuf).

- **Alcance**: WhatsApp, Telegram, Slack y Discord.
- **Protocolo**: Ingesta vía Webhook/Poll y salida vía Notificación Asíncrona.
- **Soberanía**: Mapeo estricto de identidades de canal a la autoridad del PAH.

Para los detalles técnicos de los límites de mensaje y el flujo binario, consulte el archivo de reglas [44_pervasive_channel_adapters.rules.json](44_pervasive_channel_adapters.rules.json).

---

## 2. El Adaptador de Canal (L1 Bridge)
Cada canal se implementa como un Adaptador en Layer 1 que realiza el mapeo semántico:

1.  **Normalización:** El adapter recibe el payload nativo (ej. JSON de Telegram) y lo convierte en un mensaje `io.dummie.v2.Intent`.
2.  **Context Injection:** El adapter adjunta metadatos de canal (ej. `channel_id`, `user_handle`) para que el Cerebro L2 sepa desde dónde se origina la orden.
3.  **Media Handling:** El adapter procesa imágenes o audios convirtiéndolos en referencias de `MemoryTicket` para el Palacio de Loci ([Spec 18](../L4_Edge/18_loci_ontology_mapping.md)).

---

## 3. Seguridad y Privacidad
- **Identity Pinning:** El sistema solo responde a IDs de usuario (ej. números de teléfono o handles de Telegram) registrados en la lista de autoridad del PAH.
- **End-to-End Governance:** Aunque el mensaje pase por servidores externos (WhatsApp/Telegram), el contenido sensible debe ser anonimizado o cifrado antes de salir del enclave L3 (Shield).

---

## [MSA] Sibling Components
- **Executable Contract**: [44_pervasive_channel_adapters.feature](44_pervasive_channel_adapters.feature)
- **Machine Rules**: [44_pervasive_channel_adapters.rules.json](44_pervasive_channel_adapters.rules.json)
