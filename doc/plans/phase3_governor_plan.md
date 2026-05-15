# Phase 3: The Autonomous Resource Governor (L2 Python Layer)

## Objetivo
Implementar telemetría y throttling de concurrencia a nivel de aplicación (DummieDaemon), haciendo que el motor de orquestación sea "consciente de su presión de recursos".

## Sub-Fases de Implementación (10 Pasos)

### 1. SDD Contract: Extracción de Métricas de Cgroups
- **Regla:** El motor debe leer `/sys/fs/cgroup/user.slice/.../memory.current` y `memory.max`.

### 2. TDD Baseline: Pruebas de Throttling
- **Acción:** Escribir un test unitario en Python que simule presión de memoria alta y afirme que el semáforo de concurrencia baja de 5 a 1.

### 3. Implementación: Clase `ResourceGovernor`
- **Acción:** Crear `layers/l2_brain/resource_governor.py`.

### 4. Lectura Asíncrona de Sysfs
- **Acción:** Implementar métodos no bloqueantes para leer la presión de memoria (psi) de `io.pressure` y `memory.pressure`.

### 5. Lógica de Control (PID/Thresholds)
- **Regla:** Si Memoria > 90%, `concurrency_limit = 1`. Si < 50%, `concurrency_limit = 5`.

### 6. Integración en `DummieDaemon`
- **Acción:** Inyectar el `ResourceGovernor` en el `__init__` de `DummieDaemon` en `daemon.py`.

### 7. Gobernanza de Ollama (Demand-load)
- **Acción:** El Daemon debe apagar Ollama via `systemctl --user stop ollama` (o sudo) si detecta que no hay Sagas activas por 10 minutos.

### 8. Integración con Meta-Gateway
- **Acción:** Antes de enviar una petición grande a L5 Muscle, el Gateway debe consultar al Governor si hay token budget y RAM budget.

### 9. Logging Estructurado
- **Acción:** Registrar los eventos de throttling bajo `logger.warning("[GOVERNOR] Throttling activado...")`.

### 10. TDD Verification (Integración L2)
- **Acción:** Ejecutar `pytest layers/l2_brain/tests/test_resource_governor.py`.
