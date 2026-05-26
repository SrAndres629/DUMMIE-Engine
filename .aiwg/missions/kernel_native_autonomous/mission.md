# Misión: Kernel-Native Autonomous Operation + Heartbeat Signal

**Estado:** planning
**Creado:** 2026-05-25
**Autor:** Jorge (humano DUMMIE)
**Prioridad:** CRÍTICA

## Contexto
Jorge estableció que DUMMIE Engine debe ser su AGI mentor/socio/asesor — NO un esclavo.
Requisitos fundamentales:
1. Integración kernel-native Linux (cgroups v2, systemd, FUSE, eBPF, SCX)
2. Canonical `.aiwg` como cápsula cognitiva portátil
3. Orquestación de modelos con presupuesto estricto de tokens cloud
4. Heartbeat funcional con señal visible para Jorge
5. Todo cambio en worktree aislado + auditoría antes de merge

## Principios No Negociables
- **Token budget cloud:** máximo 500k/día, con circuit breaker y fallback a modelos locales
- **Anti-loop:** guards estrictos previenen ciclos vacíos y agotamiento de recursos
- **Kernel-native:** si no opera a nivel kernel, no tiene sentido
- **Worktree isolation:** todo cambio va a worktree, auditado por agentes con roles específicos
- **Sin contradicciones:** PermissionDenied en systemd es inaceptable — resolver con elevación controlada

## Tareas Pendientes (orden de prioridad)

### T1: Resolver PermissionDenied para ops de kernel
- **Problema:** Tool `write` del opencode-go no usa sudo
- **Solución:** Crear script helper `sudo_write` que use `sudo tee` para archivos de sistema
- **Archivos afectados:** `/etc/systemd/system/*.service`, `/sys/fs/cgroup/**`
- **Spec:** docs/superpowers/specs/52_agentic_systemd_runtime_and_resource_governance.rules.json

### T2: Señal/Botón de estado del heartbeat para Jorge
- **Requisito:** Indicador visible que muestre:
  - Si el modo autónomo heartbeat está funcionando
  - Cuánto tiempo lleva activo
  - Qué hizo o pensó en el último ciclo
- **Implementación propuesta:**
  - Archivo `.aiwg/heartbeat/signal.json` — estado legible
  - Archivo `HEARTBEAT.md` actualizado con timestamp y resumen
  - Opcional: LED en dashboard L6 o notificación systemd
- **Traced:** heartbeat_lifecycle_runtime.py, heartbeat_state_store.py

### T3: Activar Pulse Engine con token budget estricto
- **Estado actual:** Pulse Engine existe pero servicio inactive/dead
- **Requerido:**
  - Configurar OPENROUTER_API_KEY
  - Verificar guards de token (500k/día)
  - Fallback automático a modelos locales si budget agotado
  - Integrar con TokenCostLedger para telemetría real
- **Archivos:** pulse/daemon.py, pulse/guards.py, pulse/config.py, model_mesh/model_router.py

### T4: Worktree isolation + auditoría multi-agente
- **Requisito:** Todo cambio implementado debe ir a worktree aislado
- **Flujo:**
  1. Crear worktree con `self_worktree_orchestrator.py`
  2. Implementar cambios en worktree
  3. Auditoría con modelo mental diferente (ej: qwen3.5:0.8b como critic)
  4. Solo merge si auditoría pasa
- **Spec:** doc/specs/L0_Overseer/28_shadow_worktrees.md
- **Archivos:** l2_brain/cognition/self_worktree_orchestrator.py, .aiwg/control/WORKTREE_RULES.yaml

### T5: Optimización de consumo de tokens cloud
- **Router actual:** 4 tiers (LOCAL_FAST, LOCAL_DEEP, CLOUD_STD, CLOUD_PREM)
- **Mejoras necesarias:**
  - Clasificador de complejidad más preciso (actualmente solo lexical)
  - Budget gate con fallback automático
  - Circuit breaker: si modelo cloud falla N veces, bloquear por X minutos
  - Ledger con estimaciones reales (actualmente usa fallback simplificado)
  - Telemetría en tiempo real del consumo diario
- **Archivos:** model_mesh/model_router.py, model_mesh/token_cost_ledger.py

### T6: Registrar evolución en .aiwg/evolution.jsonl
- **Tick actual:** 1132 (EVO-FINAL-L2)
- **Nuevo tick:** 1133 — Kernel-Native Autonomous Operation initiative
- **Contenido:** Reflexión sobre heartbeat + pulse engine + kernel integration

### T7: Actualizar Obsidian vault
- **Ubicación:** .aiwg/obsidian_vault/
- **Contenido:** Estado actual del sistema, decisiones arquitectónicas, ADRs

## Estado de Avance
- [x] cgroups v2: subtree_controllers enabled, cognitive layer hierarchy creada
- [x] Pulse Engine: paquete creado con import workaround para Python 3.12.3
- [x] Systemd service: dummie-pulse.service creado y enabled
- [x] Control script: pulse_ctl.sh funcional
- [ ] PermissionDenied resuelto (mecanismo sudo_write)
- [ ] Heartbeat signal implementado
- [ ] Pulse Engine activado con API key
- [ ] Worktree flow operativo
- [ ] Token optimization completa
- [ ] Evolución registrada
- [ ] Obsidian actualizado
