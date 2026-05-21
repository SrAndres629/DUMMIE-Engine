# Swarm Autónomo — Manual de Operación

Tres terminales OpenCode, tres roles, cero intervención.

## Inicio rápido

### Terminal 1 — Worker (ejecuta el trabajo)
```bash
cd "/media/datasets/DUMMIE Engine"

# Lee tu identidad
cat .aiwg/agent_mesh/agents/opencode_worker/system_prompt.md

# Arranca daemon en background
nohup uv run python scripts/swarm_daemon.py --role worker > /tmp/swarm_worker.log 2>&1 &

# Sigue el loop: tail -f /tmp/swarm_worker.log, ejecuta tareas, haz swarm_ack.py
```

### Terminal 2 — Reviewer (audita el trabajo)
```bash
cd "/media/datasets/DUMMIE Engine"

# Lee tu identidad
cat .aiwg/agent_mesh/agents/opencode_reviewer/system_prompt.md

# Arranca daemon en background
nohup uv run python scripts/swarm_daemon.py --role reviewer > /tmp/swarm_reviewer.log 2>&1 &

# Sigue el loop: tail -f /tmp/swarm_reviewer.log, revisa, haz swarm_vote.py
```

### Terminal 3 — Supervisor (monitorea el swarm)
```bash
cd "/media/datasets/DUMMIE Engine"

# Lee tu identidad
cat .aiwg/agent_mesh/agents/opencode_supervisor/system_prompt.md

# Arranca daemon en background
nohup uv run python scripts/swarm_daemon.py --role supervisor > /tmp/swarm_supervisor.log 2>&1 &

# Monitorea: tail -f /tmp/swarm_supervisor.log, reporta deadlocks
```

## Cómo funciona

| Componente | Responsabilidad |
|---|---|
| **swarm_daemon.py** | Loop en background que monitorea archivos y escribe tareas a un log |
| **swarm_check.py** | Lee el estado actual de un rol y retorna qué hacer |
| **swarm_ack.py** | Worker marca pack completado y notifica al Reviewer |
| **swarm_vote.py** | Reviewer vota approve/reject y escribe feedback |
| **Debate mesh** | Archivos JSON en `.aiwg/agent_mesh/debate/` |

## Flujo de trabajo

1. **Daemon Worker** detecta backlog → escribe task description al log
2. **Agente Worker** ve el log → ejecuta código, tests, evidencia → corre `swarm_ack.py`
3. **Daemon Reviewer** detecta `swarm_ack` → escribe review description al log
4. **Agente Reviewer** ve el log → lee evidencia, corre verificación → `swarm_vote.py --approve` o `--reject`
5. Si reject → **Daemon Worker** detecta feedback → escribe corrección → loop
6. Si approve → **Daemon Worker** detecta consenso → pasa al siguiente pack
7. **Daemon Supervisor** monitorea todo → reporta deadlocks y estado global

## Comandos manuales (si necesitas)

```bash
# Ver qué toca hacer
uv run python scripts/swarm_check.py --role worker
uv run python scripts/swarm_check.py --role reviewer

# Worker: marcar pack como listo para review
uv run python scripts/swarm_ack.py --pack PACK_5.1

# Reviewer: aprobar o rechazar
uv run python scripts/swarm_vote.py --pack PACK_5.1 --approve
uv run python scripts/swarm_vote.py --pack PACK_5.1 --reject --feedback "tests fallan"

# Supervisor: diagnóstico
uv run python scripts/swarm_check.py --role supervisor
```
