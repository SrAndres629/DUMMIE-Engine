# Debate Protocol — DUMMIE Canonization Swarm

## Architecture
Dos terminales OpenCode cooperan en ciclo peer-review hasta lograr consenso:

**Terminal 1 — Worker (`opencode_worker`)**
Ejecuta cada pack: implementa, verifica, produce evidencia.

**Terminal 2 — Reviewer (`opencode_reviewer`)**
Revisa la evidencia, corre verificación independiente, da feedback o vota consenso.

## Ciclo por Pack

```
Worker: implementa PACK N
  → escribe evidencia en debate/evidence/<pack>/
  → escribe mensaje en outbox/reviewer_inbox.jsonl
  → escribe su voto en debate/consensus/<pack>.json

Reviewer: lee evidencia + mensaje
  → corre verificación propia
  → si pasa: vota consensus=true en debate/consensus/<pack>.json
  → si falla: escribe crítica detallada en outbox/worker_inbox.jsonl
  
Worker: si recibió feedback
  → corrige, re-verifica
  → actualiza evidencia
  → actualiza su voto

Repetir hasta ambos consensus=true
→ PACK N cerrado → pasar a PACK N+1
```

## Auto-Organización: Propuestas

Cualquier agente puede proponer un nuevo pack cuando detecta trabajo necesario.

**Proceso:**
1. Ejecutar: `uv run python scripts/swarm_propose.py --pack PACK_N --name "..." --rationale "..." --priority [low|medium|high|critical]`
2. Los otros agentes ven la propuesta en su outbox y votan:
   - `uv run python scripts/swarm_vote_proposal.py --pack PACK_N --approve`
   - `uv run python scripts/swarm_vote_proposal.py --pack PACK_N --reject --feedback "razón"`
3. Cuando 2/3 votan approve → la propuesta se agrega automáticamente al backlog
4. El Worker lo pickea en su próximo ciclo

**Cuándo proponer:**
- Worker: al terminar un pack, si ve trabajo adicional necesario
- Reviewer: durante la review, si detecta gaps que el Worker no cubrió
- Supervisor: al detectar deadlocks, estancamiento, o trabajo estructural evidente

**Prioridades:**
- `critical`: bloquea otros packs, requiere atención inmediata
- `high`: debe hacerse pronto, dependencia de trabajo futuro
- `medium`: mejora deseable
- `low`: nice-to-have, hacer cuando haya tiempo

## Reglas del Debate

1. **Worker no puede declarar un pack complete sin evidencia**: tests pasados, production verification, spec registry, diff limpio de los archivos tocados.
2. **Reviewer no puede votar consensus sin correr verificación propia**: no confiar en la evidencia del Worker, correr los comandos.
3. **Si hay desacuerdo después de 3 rondas**: el Reviewer escribe `deadlock: true` en el consensus y el Worker debe pedir intervención humana.
4. **Cada pack debe tener spec registry sync al final**: `error_count=0`.
5. **No mover al siguiente pack hasta que el actual esté cerrado**.
6. **Cualquier agente puede proponer nuevos packs en cualquier momento**. No esperar instrucciones humanas.

## Evidencia Requerida por Pack

Cada pack debe producir en `debate/evidence/<pack>/`:
- `tests.txt` — salida completa de `pytest -q` sobre la suite relevante
- `production_verification.json` — salida del ProductionVerificationHook
- `spec_registry.txt` — `spec_count` y `error_count`
- `diff_summary.txt` — `git diff --stat` de los archivos tocados
- `diff_check.txt` — `git diff --check` de los archivos tocados (debe salir limpio)
- `notes.md` — notas del Worker sobre lo que hizo

## Backlog (orden de packs)

Consultar en `.aiwg/agent_mesh/debate/backlog.json`

## Consenso Actual

Consultar en `.aiwg/agent_mesh/debate/consensus/`
