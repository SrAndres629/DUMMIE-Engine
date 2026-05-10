---
skill_id: "ao.v2.diag.system_sanity"
version: "1.0.0"
description: "Diagnóstico proactivo de la salud del Agentic OS (SDD, NATS, SHM)."
author: "sw.auditor"
capabilities:
  - "sdd_integrity_check"
  - "nats_mesh_latency_test"
  - "shm_offset_validation"
requirements:
  layers: ["L0", "L1", "L3"]
  tools: ["python3", "nats-pub", "doc/sdd_validator.py"]
  dependencies: ["DE-V2-L1-41"]
invariants:
  - "no_network_access: true"
  - "read_only: true"
---

# Skill: System Sanity Diagnosis 🛠️

## Context
Esta habilidad permite al agente realizar una auditoría de "Línea Detenida" (Jidoka) para asegurar que el entorno de fabricación es coherente antes de iniciar una fase de implementación.

## 1. Instructions
1.  **SDD Check:** Ejecuta el `sdd_validator.py` sobre el monorepo actual.
2.  **Bus Check:** Emite un `ao.v2.l0.signal.pulse` y espera a que el Router L1 responda (Ack).
3.  **Memory Check:** Valida que la firma `ATKN` (Magic Bytes) esté presente en el offset `0x00` del SHM.

## 2. Acceptance Criteria (BDD)
```gherkin
Feature: System Sanity Skill
  Scenario: Run full architectural audit
    Given the environment is initialized
    When the "System Sanity" skill is invoked
    Then the SDD Validator must return "OK"
    And the SHM Checksum must match the computed CRC32
    And the current Token Budget (E-Shield) must be > 0.
```
