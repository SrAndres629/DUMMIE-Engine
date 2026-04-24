---
spec_id: "DE-V2-L3-45"
title: "Protocolo de Emparejamiento Seguro (Sovereign Node Pairing)"
status: "ACTIVE"
version: "2.2.0"
layer: "L3"
namespace: "io.dummie.v2.shield.trust"
authority: "PAH"
dependencies:
  - id: "DE-V2-L1-23"
    relationship: "GOVERNS"
  - id: "DE-V2-L1-41"
    relationship: "HANDSHAKES_OVER"
tags: ["shield", "security", "node_pairing", "zero_trust"]
---

# 45. Protocolo de Emparejamiento Seguro (Sovereign Node Pairing)

## Abstract
Inspirado por el **Pairing Ritual de OpenClaw**, esta especificación establece la frontera de confianza para la integración de hardware físico distribuido. Ningún nodo puede unirse al sistema nervioso (L1) sin una aprobación explícita y soberana del PAH, garantizando un entorno de ejecución Zero-Trust donde la identidad del hardware es validada y fijada (Pinning).

## 1. Cognitive Context Model (Ref)
Para el flujo de aprobación (Quarantine, Pending, Approval), los requisitos de cabeceras (Handshake Signature, Hardware ID) y la política de rotación de tokens (TTL 24h), consulte el archivo hermano [45_secure_node_pairing_protocol.rules.json](./45_secure_node_pairing_protocol.rules.json).

---

## 2. El Ritual de Confianza (Handshake)
Cuando un nuevo dispositivo intenta conectarse, el Escudo L3 ejecuta el siguiente protocolo:
1.  **Isolation:** El socket entra en estado de cuarentena estricta.
2.  **Challenge-Response:** Desafío criptográfico basado en el Hardware ID del dispositivo.
3.  **Human Gate:** Notificación al PAH vía canal pervasivo ([Spec 44](../L1_Nervous/44_pervasive_channel_adapters.md)).
4.  **Identity Fixation:** Una vez aprobado, se genera un token de sesión inmutable y se fija el perfil de hardware para prevenir suplantaciones.

---

## 3. Invariantes de Seguridad
- **No Auto-Pairing:** Se prohíbe el emparejamiento automático por proximidad o descubrimiento mDNS.
- **Hardware Drift Detection:** Cualquier cambio significativo en el perfil de hardware del dispositivo revoca instantáneamente el token de sesión.
- **Ephemeral Keys:** Las llaves de cifrado de transporte son rotatorias y nunca se almacenan en disco de forma persistente fuera de la enclave segura.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [45_secure_node_pairing_protocol.feature](./45_secure_node_pairing_protocol.feature)
- **Machine Rules:** [45_secure_node_pairing_protocol.rules.json](./45_secure_node_pairing_protocol.rules.json)
