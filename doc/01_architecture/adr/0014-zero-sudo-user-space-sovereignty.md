---
spec_id: "DE-V2-[ADR-0014](0014-zero-sudo-user-space-sovereignty.md)"
title: "Soberanía de Usuario y Ejecución Zero-Sudo"
status: "PROPOSED"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-[ADR-0006](0006-sovereign-hybrid-documentation-protocol.md)"
    relationship: "REINFORCES"
tags: ["architectural_decision", "security", "permissions", "user_space"]
---

# [ADR-0014](0014-zero-sudo-user-space-sovereignty.md): Soberanía de Usuario y Ejecución Zero-Sudo

## Abstract
DUMMIE Engine debe ser capaz de operar en entornos restringidos donde el acceso a `sudo` no está disponible o está estrictamente auditado. Esta decisión establece que todas las herramientas de fabricación, agentes de IA y procesos de compilación deben residir y ejecutarse exclusivamente en el espacio de usuario (User-Space).

## 1. Contexto
Muchos agentes de IA y entornos de desarrollo modernos (como los sandboxes de Antigravity o entornos corporativos) bloquean el acceso a comandos de administración. El uso de `sudo` para instalar dependencias o gestionar Docker rompe la hermeticidad del sistema y crea fricción operativa.

## 2. Decisión: Aislamiento Total en Espacio de Usuario

Se imponen las siguientes reglas obligatorias:

### 2.1. Gestión de Herramientas (Tooling)
- **Prohibición de Instalación Global:** Ningún script del motor debe intentar usar `apt`, `dnf` o similares.
- **Instalación en `$HOME/.local`:** Todas las herramientas (Go, Zig, Elixir, Rust) deben instalarse en el directorio personal del usuario o dentro del propio monorepo.
- **Uso Obligatorio de `uv`:** Para Python, se prohíbe el uso de `pip` global. Todas las dependencias deben gestionarse vía `uv sync` en entornos virtuales locales.

### 2.2. Virtualización y Contenedores
- **Docker Rootless:** Se recomienda el uso de Docker en modo rootless o asegurar que el usuario pertenezca al grupo `docker`.
- **Alternativas a Docker:** Si Docker no está disponible sin `sudo`, los agentes deben caer en modo "Host Local" usando las herramientas instaladas en espacio de usuario.

### 2.3. Configuración de Agentes (MCP)
- Los servidores MCP deben configurarse para usar los binarios localizados en el PATH del usuario, priorizando las versiones locales del proyecto.

## 3. Consecuencias
- **Positivas:** Mayor seguridad, portabilidad instantánea entre sistemas Linux, compatibilidad total con agentes de IA sandboxed.
- **Negativas:** El usuario debe realizar una configuración inicial de PATH más cuidadosa. Requiere más espacio en el disco del usuario al duplicar herramientas que podrían estar instaladas globalmente.

---

## [MSA] Sibling Components Requeridos
- **Machine Rules:** `0014-zero-sudo-user-space-sovereignty.rules.json`
