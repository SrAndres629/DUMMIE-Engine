---
spec_id: "DE-V2-L3-45"
title: "Protocolo de Emparejamiento Seguro (Sovereign Node Pairing)"
status: "ACTIVE"
version: "1.0.0"
layer: "L3"
namespace: "io.dummie.v2.shield.trust"
authority: "PAH"
dependencies:
  - id: "DE-V2-L1-23"
    relationship: "GOVERNS"
  - id: "DE-V2-L1-41"
    relationship: "HANDSHAKES_OVER"
tags: ["shield", "security", "node_pairing", "zero_trust", "claw_ism"]
---

# 45. Protocolo de Emparejamiento Seguro (Sovereign Node Pairing)

## Abstract
Inspirado por el **Pairing Ritual de OpenClaw**, esta especificación establece la frontera de confianza para la integración de hardware físico distribuido. Ningún nodo (móvil, laptop, servidor remoto) puede unirse al sistema nervioso (L1) sin una aprobación explícita y soberana del Puntero de Autoridad Humana (PAH), garantizando un entorno de ejecución Zero-Trust.

## 1. El Ritual de Confianza
El emparejamiento de nodos es la frontera de seguridad física de la SFE. Su objetivo es garantizar que solo hardware explícitamente autorizado pueda interactuar con el sistema nervioso central.

- **Flujo**: Captura en Cuarentena -> Notificación al PAH -> Firma Manual -> Emisión de Token.
- **Seguridad**: Uso de tokens rotatorios (TTL 24h) y revocación instantánea vía veto soberano.

Para los detalles técnicos del protocolo de handshake y las políticas de rotación, consulte el archivo de reglas [45_secure_node_pairing_protocol.rules.json](45_secure_node_pairing_protocol.rules.json).

---

## 2. El Ritual de Emparejamiento (Handshake)
Cuando un nodo intenta conectarse al Gateway L1, el Escudo L3 interviene:

1.  **Isolation:** El socket se mantiene en un estado de "Cuarentena" donde solo se permiten señales de identificación básica.
2.  **Challenge:** El sistema emite un desafío criptográfico al nodo.
3.  **Human Gate:** Se genera una `PendingConfirmation` que bloquea la integración hasta que el PAH firme la entrada.
4.  **Identity Crystalization:** Una vez aprobado, el nodo recibe su identidad única en el Palacio de Loci ([Spec 18](../L4_Edge/18_loci_ontology_mapping.md)).

---

## 3. Invariantes de Seguridad
- **Forbidden Pairing:** Se prohíbe el emparejamiento automático por proximidad (ej. Bluetooth/mDNS) sin confirmación manual.
- **Hardware Pinning:** Si un nodo cambia drásticamente su perfil de hardware (CPU/RAM ID), el token es revocado automáticamente por sospecha de suplantación.

---

## [MSA] Sibling Components
- **Executable Contract**: [45_secure_node_pairing_protocol.feature](45_secure_node_pairing_protocol.feature)
- **Machine Rules**: [45_secure_node_pairing_protocol.rules.json](45_secure_node_pairing_protocol.rules.json)
