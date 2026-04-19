---
spec_id: "DE-V2-L0-48"
title: "Protocolo de Cristalización de Integridad Arquitectónica (ACIP)"
status: "ACTIVE"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.overseer.integrity"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-06"
    relationship: "REFINES"
tags: ["governance", "integrity", "acip", "industrial_sdd"]
---

# Spec 48: Protocolo de Cristalización de Integridad Arquitectónica (ACIP)

## 1. Declaración de Misión
El objetivo de esta especificación es asegurar que el **DUMMIE Engine** sea un sistema de auto-documentación perpetua, donde ninguna decisión física (código/infra) quede huérfana de su justificación teórica (SDM/SDD). Se prohíbe la acumulación de "Deuda de Conocimiento".

## 2. Los Tres Pilares de la Integridad

### 2.1. Cristalización Mandataria (Causal Crystallization)
Tras cada hito de implementación exitosa (Phase-Gate), el agente ejecutor DEBE:
1.  **Registrar la Decisión**: En `.aiwg/memory/decisions.jsonl` (Por qué se hizo así).
2.  **Registrar la Lección**: En `.aiwg/memory/lessons.jsonl` (Qué falló y cómo se evitó).
3.  **Resolver Ambigüedades**: En `.aiwg/memory/ambiguities.jsonl` (Qué compromisos pragmáticos se tomaron).

### 2.2. Política de Soberanía de Disco (Anti-Bloatware)
La unidad de sistema operativo (Linux Main) es sagrada y solo debe contener **CÓDIGO FUENTE E INTENCIÓN**.
- **Regla**: Todo artefacto derivado (venvs, node_modules, caches, build-artifacts) superior a 50MB DEBE residir en la **Unidad D (/media/datasets)**.
- **Mecanismo**: Uso obligatorio de enlaces simbólicos (symlinks) gestionados por el protocolo de soberanía.
- **Excepción**: Solo archivos `.env` y archivos de configuración crítica de menos de 10KB pueden residir en la raíz local.

### 2.3. Control de Drift (Sincronización SDD)
Si la implementación física diverge de la Spec (ej. usar Docker en lugar de Nix debido a restricciones de sistema), la Spec DEBE ser actualizada con una sección de "Compromisos de Runtime" antes de cerrar la sesión.

## 3. Criterios de Aceptación (AC)
- **AC-48.1**: Todo agente futuro debe ser capaz de reconstruir el entorno políglota leyendo solo la Spec 08 y los registros de memoria de la sesión anterior.
- **AC-48.2**: El comando `du -sh .` en el monorepo no debe exceder los 500MB (excluyendo el historial de Git).
- **AC-48.3**: No existe código sin contrato (Spec 10) ni contrato sin registro de decisión (Spec 34).

## 4. Gobernanza
Cualquier desviación de este protocolo será marcada como `CRITICAL_ARCHITECTURE_VIOLATION` por el Sentinel (L3) y bloqueará el despliegue en producción.
