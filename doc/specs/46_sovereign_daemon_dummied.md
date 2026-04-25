---
spec_id: "DE-V2-L0-46"
title: "Demonio Soberano (dummied)"
status: "PROPOSAL"
layer: "L0"
last_verified_on: "2026-04-25"
---
# Especificación: Demonio Soberano (dummied)

## 1. Propósito
Definir el comportamiento de un servicio persistente que orqueste el enjambre de agentes de forma autónoma, asíncrona y resiliente a reinicios del sistema.

## 2. Invariantes Operativos
- **Sovereignty**: El daemon es el único dueño del ciclo de vida de los agentes locales.
- **Persistence**: Todo cambio en el `State` de una rama debe persistirse atómicamente antes de cada paso del grafo.
- **Async-First**: La comunicación con el humano (vía L1/Telegram) no bloquea el progreso de ramas paralelas.
- **Resilience**: Tras un fallo de energía o crash del proceso, el daemon debe recuperar el estado exacto de la última instrucción válida.

## 3. Estados del Proceso
- `IDLE`: Sin tareas activas.
- `ACTIVE`: Al menos una rama ejecutando un agente.
- `DEGRADED`: Fallo en la comunicación con el Memory Plane (L1) o el StateStore.
- `SHUTDOWN`: Cierre controlado salvando todos los estados pendientes.

## 4. Interfaz de Control (Contrato Sugerido)
El daemon expondrá un canal de control con los siguientes comandos:
- `SPAWN(goal)`: Crea una nueva raíz de orquestación.
- `STATUS()`: Retorna el mapa de fricción actual del enjambre.
- `WAKE(branch_id, context_patch)`: Reanuda una rama suspendida inyectando nueva información.
- `TERMINATE(branch_id)`: Poda una rama del grafo.

## 5. Evidencia Física
- `layers/l0_overseer/cmd/dummied/main.go`
- `layers/l0_overseer/internal/orchestrator/store.go`
- `layers/l0_overseer/internal/orchestrator/daemon.go`
- `.aiwg/memory/state.db` (SQLite)
