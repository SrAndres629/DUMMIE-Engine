# Phase 1: Cgroups & OS Slicing (Agentic Slice Integration)

## Objetivo
Cumplir la Spec 52 implementando una topología jerárquica de Systemd (vía Cgroups v2) que limite y agrupe los recursos de CPU/Memoria de todos los agentes autónomos locales, incluyendo Ollama y DUMMIE Engine.

## Sub-Fases de Implementación (10 Pasos)

### 1. SDD Contract: Definición de `agentic.slice`
- **Regla:** La tajada principal debe tener límites lógicos de memoria (high/max) para proteger la sesión del usuario.
- **Acción:** Definir las propiedades de Systemd (`MemoryHigh`, `MemoryMax`, `CPUWeight`).

### 2. TDD Baseline: Tests de Infraestructura L0
- **Regla:** Ningún cambio sin un test previo (Red-Green-Refactor).
- **Acción:** Crear `scripts/tests/test_cgroup_hierarchy.sh` para afirmar que `agentic.slice` no existe actualmente.

### 3. Implementación Local: Archivos de Systemd
- **Acción:** Generar `agentic.slice` y `agentic-agent@.service` dentro de `scripts/systemd/` para revisión en espacio de usuario.

### 4. SDD Contract: Subyugación de Ollama
- **Regla:** Ollama debe correr *dentro* de `agentic.slice`.
- **Acción:** Diseñar el override de Systemd (`99-agentic.conf`).

### 5. Implementación Local: Ollama Override
- **Acción:** Generar `99-agentic.conf` en `scripts/systemd/ollama.service.d/`.

### 6. Despliegue de Sistema (System Deployment)
- **Acción:** Crear un instalador idempotente `scripts/install_phase1_systemd.sh` (requerirá `sudo` del usuario).

### 7. Integración de DUMMIE Engine al Slice
- **Acción:** Actualizar `dummie-engine.service` para enrutar el tráfico al nuevo slice del sistema operativo.

### 8. Activación de Reglas de Delegación (Systemd User Delegation)
- **Acción:** Configurar el host para permitir que el usuario delegue Cgroups.

### 9. Integración Global de Comandos
- **Acción:** Actualizar scripts de inicio para que los comandos hereden las restricciones cgroups automáticamente.

### 10. TDD Verification (Green Phase)
- **Acción:** Ejecutar `test_cgroup_hierarchy.sh` pos-despliegue para verificar Cgroup V2 accounting.
