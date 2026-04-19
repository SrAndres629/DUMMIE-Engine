---
spec_id: "DE-V2-L3-47"
title: "Protocolo de Inyección de Secretos Soberano (Vault Shield)"
status: "ACTIVE"
version: "1.0.0"
layer: "L3"
namespace: "io.dummie.v2.shield.secrets"
authority: "PAH"
dependencies:
  - id: "DE-V2-L3-04"
    relationship: "GOVERNS"
  - id: "DE-V2-L1-44"
    relationship: "HYDRATES_VIA"
tags: ["shield", "security", "secret_management", "blind_injection", "claw_ism"]
---

# 47. Protocolo de Inyección de Secretos Soberano (Vault Shield)

## Abstract
Inspirado por las arquitecturas de **Hardened Gateways (OpenClawd)**, esta especificación introduce el concepto de **Ceguera Cognitiva de Secretos**. Para prevenir la fuga de credenciales sensibles (API Keys, SSH Keys, Tokens) por parte de agentes comprometidos o alucinaciones, el Cerebro L2 nunca opera sobre secretos reales, sino sobre **Placeholders Soberanos** que solo se resuelven en los límites del sistema (Boundaries).

## 1. El Concepto de Ceguera Cognitiva
La Ceguera Cognitiva es un mecanismo de defensa que impide que el Cerebro L2 tenga acceso a secretos reales. Toda credencial se maneja mediante alias, garantizando que el LLM nunca "vea" el secreto, ni siquiera accidentalmente en su ventana de contexto.

- **Arquitectura**: Enclave cifrado en L3 (Vault) con inyección por marcadores de posición (Placeholders).
- **Ciclo de Vida**: El agente usa `$VAULT_*`; la hidratación ocurre en la salida física (L1/L5) fuera de la zona de razonamiento.
- **Privacidad**: Scrubbing automático de logs para detectar y censurar cualquier intento de fuga.

Para los detalles técnicos del cifrado del enclave y los protocolos de sustitución de cadena en el borde, consulte el archivo de reglas [47_sovereign_secret_injection_protocol.rules.json](47_sovereign_secret_injection_protocol.rules.json).

---

## 2. El Ritual de Inyección Blindada
El sistema garantiza que ningún secreto toque el contexto del LLM:

1.  **Vault Definition:** El PAH define los secretos en el monorepo (ej: `.env.secret` cifrado o servicio Vault).
2.  **Cognitive Masking:** Cuando el agente L2 requiere una credencial, el `S-Shield` ([Spec 04](04_anti_ignorance_shields.md)) inyecta el placeholder correspondiente (`$VAULT_GITHUB_TOKEN`).
3.  **Boundary Hydration:** Solo cuando el `Intent` se traduce en una acción física (ej: una petición REST o un comando Shell), los adaptadores de **Layer 1** o **Layer 5** interceptan la cadena y sustituyen el placeholder por el valor real fuera del alcance del Cerebro.
4.  **Leak Prevention:** Si el agente intenta imprimir el valor del secreto, solo recibirá la cadena literal del placeholder.

---

## 3. Auditoría y Revocación
- **Scrubbing Invariante:** El Auditor Semántico ([sdd_validator.py](../../04_forge/sdd_validator.py)) escanea los logs de telemetría en busca de patrones que coincidan con secretos reales, activando una **Alerta de Necrosis** inmediata si se detecta una fuga.
- **Scope Restriction:** Los secretos están mapeados a agentes específicos. Un agente de "Investigación" no puede invocar placeholders de "Implementación".

---

## [MSA] Sibling Components
- **Executable Contract**: [47_sovereign_secret_injection_protocol.feature](47_sovereign_secret_injection_protocol.feature)
- **Machine Rules**: [47_sovereign_secret_injection_protocol.rules.json](47_sovereign_secret_injection_protocol.rules.json)
