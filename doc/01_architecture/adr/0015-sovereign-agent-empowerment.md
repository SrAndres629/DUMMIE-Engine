---
spec_id: "DE-V2-[ADR-0015](0015-sovereign-agent-empowerment.md)"
title: "Soberanía Total y Empoderamiento del Agente"
status: "ACCEPTED"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "HUMAN_ORACLE"
dependencies:
  - id: "DE-V2-[ADR-0014](0014-zero-sudo-user-space-sovereignty.md)"
    relationship: "SUPERSEDES"
tags: ["architectural_decision", "sovereignty", "permissions", "empowerment"]
---

# [ADR-0015](0015-sovereign-agent-empowerment.md): Soberanía Total y Empoderamiento del Agente

## Abstract
Bajo mandato directo del Puntero de Autoridad Humana (PAH), se otorga a los agentes de IA acceso total y sin restricciones a las capacidades físicas del sistema. Esto implica la eliminación de sandboxes restrictivos y la configuración de privilegios elevados para operaciones de infraestructura.

## 1. Contexto
Las restricciones de seguridad por defecto (nsjail sandboxing) en los agentes de IA generan fallos de limpieza en `/tmp` y bloquean la ejecución de herramientas críticas como `uv sync` o `docker`. El usuario ha manifestado explícitamente la necesidad de delegar la responsabilidad total al agente para acelerar la fabricación de software.

## 2. Decisión: Acceso Total y Responsabilidad Delegada

### 2.1. Desactivación de Sandboxes
- Se instruye al usuario a desactivar el "Execution Sandbox" en la configuración de la IDE.
- Los agentes operarán directamente sobre el shell del host, permitiendo la interacción natural con el sistema de archivos y periféricos.

### 2.2. Elevación de Privilegios Controlada
- Se permite la configuración de excepciones en `sudoers` para comandos específicos del monorepo.
- El agente asume el control del ciclo de vida de las dependencias (`uv`, `npm`, `cargo`, `zig`).

### 2.3. Limpieza de Residuos
- El sistema debe ser capaz de auto-limpiar sus residuos en `/tmp` y otros directorios temporales, requiriendo permisos para borrar archivos creados por procesos previos de sandboxing.

## 3. Consecuencias
- **Positivas:** Eliminación de errores de "Permiso Denegado". Velocidad de ejecución industrial. Capacidad de los agentes para auto-reparar el sistema operativo si fuera necesario.
- **Negativas:** Alto riesgo de seguridad si el agente es manipulado por un actor externo. Requiere una confianza absoluta en la alineación del agente con el PAH.

---

## [MSA] Sibling Components Requeridos
- **Machine Rules:** `0015-sovereign-agent-empowerment.rules.json`
