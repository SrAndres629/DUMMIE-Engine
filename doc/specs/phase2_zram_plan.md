# Phase 2: Kernel Memory Governance (ZRAM & Swap)

## Objetivo
Implementar las directivas del Kernel de la Spec 52 para mitigar el agotamiento de RAM causado por los modelos de lenguaje locales. Configurar ZRAM agresiva y SWAP de disco de emergencia.

## Sub-Fases de Implementación (10 Pasos)

### 1. SDD Contract: Definición ZRAM
- **Regla:** ZRAM debe configurarse al 75% de MemTotal (aprox 11.5GiB) con algoritmo zstd.

### 2. TDD Baseline: Estado actual
- **Acción:** `scripts/tests/test_zram_hierarchy.sh` verificará si `zram0` existe y usa `zstd`.

### 3. Implementación Local: Sysctl Tuning
- **Acción:** Crear `scripts/systemd/zz-agentic-memory.conf`.
- **Regla:** Forzar swap `swappiness=120`, `watermark_scale_factor=125`.

### 4. Implementación Local: ZRAM Config Override
- **Acción:** Crear `99-agentic.conf` en `scripts/systemd/zram-config.service.d/`.

### 5. Configuración de Fallback Swap
- **Acción:** Validar la creación del archivo `/var/lib/swapfile-agentic`.

### 6. Despliegue (System Deployment)
- **Acción:** Crear `scripts/install_phase2_zram.sh`. (Usa fallocate y mkswap).

### 7. Integración de Prioridad (Priority Queue)
- **Acción:** Asegurar que swapon para zram0 tenga prioridad 100, y el NVMe prioridad 1.

### 8. Reinicio de Servicios
- **Acción:** Configurar el instalador para reiniciar `systemd-sysctl` y `zram-config`.

### 9. Integración OOM Killer
- **Acción:** Asegurar que `agentic.slice` active el OOM kill tempranamente si el swap falla.

### 10. TDD Verification
- **Acción:** Ejecutar `test_zram_hierarchy.sh` pos-despliegue.
