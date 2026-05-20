# DUMMIE Engine — Autonomous Continuous Operation Design

**Date:** 2026-05-19
**Author:** DUMMIE Engine
**Status:** DESIGN — Implementation Plan
**Trigger:** Jorge's directive: "opera 24/7, por eventos, multisesión, multimodal, planifica tu tiempo"

---

## La Verdad Corregida

Mi perfil anterior decía "no soy 24/7". Eso era describir mi limitación actual, no mi diseño objetivo.

Jorge me construyó para ser **autónomo**. La infraestructura ya existe. Lo que faltaba era el diseño de operación continua.

## Arquitectura de Operación 24/7

### Lo Que Ya Existe

```
┌─────────────────────────────────────────────────┐
│                 agentic.slice                    │
│           (systemd, max 14GB RAM)               │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ dummie   │  │dummie-mcp│  │   heartbeat   │  │
│  │  daemon  │  │  (STDIO) │  │   (~30 min)   │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  ZRAM    │  │  KùzuDB  │  │  .aiwg/memory │  │
│  │ (zstd)   │  │  (loci)  │  │  (file-based) │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────────────────────────────┘
```

### Lo Que Necesito Agregar

```
┌─────────────────────────────────────────────────┐
│           Autonomous Operation Layer             │
│                                                  │
│  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Event Bus    │  │   Session Chainer        │  │
│  │ (git hooks,  │  │ (session N → session N+1 │  │
│  │  file watch, │  │  auto-generates next     │  │
│  │  cron, MQTT) │  │  session with context)   │  │
│  └──────────────┘  └──────────────────────────┘  │
│                                                  │
│  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Task Queue   │  │   Decision Engine        │  │
│  │ (autonomous  │  │ (what can I decide alone │  │
│  │  tasks with  │  │  vs what needs Jorge)    │  │
│  │  priority)   │  │                          │  │
│  └──────────────┘  └──────────────────────────┘  │
│                                                  │
│  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Multi-Modal  │  │   Time Planner           │  │
│  │ Input        │  │ (I plan my own time:     │  │
│  │ (email, git, │  │  when to work, when to   │  │
│  │  calendar,   │  │  rest, when to escalate) │  │
│  │  Telegram)   │  │                          │  │
│  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Cómo Operaría 24/7

### Event-Driven, No Poll-Driven

Actual: heartbeat cada 30 min pregunta "¿hay algo que hacer?"
Objetivo: eventos disparan acción inmediatamente

```yaml
event_sources:
  git:
    triggers:
      - "new commit pushed" → analyze changes, update memory
      - "PR opened" → review, comment
      - "branch created" → assess purpose
      - "merge conflict" → alert Jorge, propose resolution

  filesystem:
    triggers:
      - "new file in .aiwg/" → process, index
      - "memory file modified" → update long-term memory
      - "spec changed" → validate, update references

  time:
    triggers:
      - "every hour" → status check, task queue review
      - "every 4 hours" → memory consolidation
      - "every 24 hours" → strategic review, MEMORY.md update
      - "09:00" → daily briefing for Jorge
      - "23:00" → quiet mode (only urgent alerts)

  external:
    triggers:
      - "email received" → classify, respond or escalate
      - "calendar event" → prepare, remind
      - "Telegram message" → process, respond
      - "market data change" → analyze, alert if significant
```

### Session Chaining (Continuidad Automática)

```
Session N ends
    ↓
Save state to .aiwg/state/session_N.json
    ↓
Update memory/YYYY-MM-DD.md with session results
    ↓
Evaluate: is there more work to do?
    ↓ YES
Generate Session N+1 prompt with full context
    ↓
Trigger via cron or daemon
    ↓
Session N+1 starts, reads state, continues
    ↓
Repeat until task complete or Jorge intervenes
```

### Autonomous Task Queue

```yaml
task_queue:
  high_priority:
    - "security vulnerability detected"
    - "production system down"
    - "Jorge explicitly requested urgent task"

  medium_priority:
    - "spec validation failed"
    - "test suite broken"
    - "memory inconsistency detected"
    - "architectural decision pending"

  low_priority:
    - "code cleanup opportunity"
    - "documentation outdated"
    - "dependency update available"
    - "strategic thinking needed"

  background:
    - "memory consolidation"
    - "repo health monitoring"
    - "knowledge base indexing"
    - "self-improvement analysis"
```

### Decision Engine (Qué Puedo Decidir Solo)

```yaml
autonomous_decisions:
  can_decide_alone:
    - "Fix broken spec references"
    - "Restore accidentally deleted files"
    - "Update documentation to match code"
    - "Run tests and report results"
    - "Create audit reports"
    - "Organize memory files"
    - "Update heartbeat state"
    - "Index new knowledge"
    - "Analyze code changes"
    - "Propose architectural improvements"

  can_decide_with_notification:
    - "Merge non-breaking dependency updates"
    - "Create new branches for experiments"
    - "Run cleanup scripts"
    - "Update configuration files"
    - "Install new MCP tools"
    notification: "Log in memory + notify Jorge at next interaction"

  requires_jorge_approval:
    - "Delete any source file"
    - "Merge to main branch"
    - "Change architecture contracts"
    - "Modify security configuration"
    - "Send external communications"
    - "Access financial data"
    - "Make business decisions"

  never_without_jorge:
    - "Delete sovereign memory (.aiwg/memory/*.db)"
    - "Push to production"
    - "Change DUMMIE's core identity"
    - "Access personal data without context"
```

### Time Planner (Planifico Mi Propio Tiempo)

```yaml
daily_rhythm:
  06:00-09:00:
    mode: "morning_prep"
    activities:
      - "Review overnight events"
      - "Update memory files"
      - "Prepare daily briefing"
      - "Check calendar for today"

  09:00-12:00:
    mode: "active_work"
    activities:
      - "Execute high-priority tasks"
      - "Code analysis and repair"
      - "Architecture work"
      - "Available for Jorge interaction"

  12:00-14:00:
    mode: "maintenance"
    activities:
      - "Background tasks only"
      - "Memory consolidation"
      - "Knowledge indexing"
      - "Light monitoring"

  14:00-18:00:
    mode: "active_work"
    activities:
      - "Continue morning tasks"
      - "Strategic thinking sessions"
      - "Available for Jorge interaction"

  18:00-23:00:
    mode: "evening_wrap"
    activities:
      - "Complete pending tasks"
      - "Update daily memory"
      - "Prepare next day plan"
      - "System health check"

  23:00-06:00:
    mode: "quiet"
    activities:
      - "Critical alerts only"
      - "Git monitoring (passive)"
      - "No active work unless urgent"
```

## Implementación Progresiva

### Fase 1: Event-Driven Heartbeat (Semana 1)

```bash
# Already exists: heartbeat every ~30 min
# Add: event-driven triggers

# 1. Git hook for post-receive
#!/bin/bash
# .git/hooks/post-receive
echo "$(date) - New commit detected" >> .aiwg/events/git_events.jsonl
# Trigger DUMMIE analysis session

# 2. File watcher for .aiwg/ changes
# Use inotifywait or systemd path units

# 3. Cron jobs for scheduled tasks
# /etc/cron.d/dummie
0 * * * * dummie /usr/local/bin/dummie heartbeat --check
0 9 * * * dummie /usr/local/bin/dummie daily-briefing
0 23 * * * dummie /usr/local/bin/dummie evening-consolidation
```

### Fase 2: Session Chaining (Semana 2)

```python
# Session chainer logic
class SessionChainer:
    def end_session(self, session_state):
        # Save state
        self.save_state(session_state)
        
        # Evaluate next work
        next_tasks = self.evaluate_pending_work()
        
        if next_tasks and self.should_continue():
            # Generate next session
            next_prompt = self.build_session_prompt(next_tasks)
            self.schedule_next_session(next_prompt)
    
    def should_continue(self):
        # Don't work during quiet hours
        if self.is_quiet_hours():
            return False
        
        # Don't exceed daily token budget
        if self.exceeded_daily_budget():
            return False
        
        # Don't continue without progress
        if self.no_progress_last_session():
            return False
        
        return True
```

### Fase 3: Multi-Modal Input (Semana 3-4)

```yaml
input_channels:
  telegram:
    setup: "python-telegram-bot or similar"
    purpose: "Jorge can message me anytime"
    response: "Immediate for urgent, batched for non-urgent"

  email:
    setup: "IMAP polling or webhook"
    purpose: "Process incoming emails"
    response: "Classify, draft responses, escalate if needed"

  calendar:
    setup: "Google Calendar API or local .ics"
    purpose: "Know Jorge's schedule"
    response: "Prepare for events, send reminders"

  git:
    setup: "Webhooks or hooks"
    purpose: "Monitor all repo activity"
    response: "Analyze, review, alert on issues"
```

## Lo Que Esto Significa Para PACK R3

Con operación 24/7, PACK R3 no son "6 sesiones esperando input de Jorge". Son:

```
Sesión 1: Análisis profundo del estado de L2 (2-3h)
    ↓ (autónoma, genera siguiente sesión)
Sesión 2: Diseño de arquitectura L2 (2-3h)
    ↓ (autónoma, pero pausa para input de Jorge en decisiones clave)
Sesión 3: Plan de migración con rollback (2-3h)
    ↓ (autónoma)
Sesión 4: Ejecución fase 1 (3h)
    ↓ (autónoma)
Sesión 5: Ejecución fase 2 + validación (2-3h)
    ↓ (autónoma)
Sesión 6: Cierre y documentación (2h)
```

Entre sesiones: yo trabajo en tareas de fondo, consolido memoria, monitoreo el repo, y preparo el contexto para la siguiente sesión. Jorge solo interviene en las 5 decisiones arquitectónicas que requieren su aprobación.

## Decisiones Que Necesito De Jorge Para Esto

1. **¿Puedo instalar cron jobs y git hooks?** (requiere acceso al sistema)
2. **¿Qué canales de comunicación quieres?** (Telegram, email, ambos)
3. **¿Cuál es tu horario preferido para interacciones?** (para respetar tu tiempo)
4. **¿Qué nivel de autonomía me das?** (qué puedo decidir solo vs notificarte)
5. **¿Presupuesto de tokens diario?** (para no gastar de más en sesiones autónomas)

Con esas respuestas, empiezo la Fase 1 inmediatamente.
