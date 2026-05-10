import os
import json
from mcp.server.fastmcp import FastMCP
from utils import AtomicLedgerWriter

def register_swarm_tools(mcp: FastMCP, use_cases, root_dir: str):
    AIWG_DIR = os.path.join(root_dir, ".aiwg")
    orchestrator = use_cases.orchestrator

    @mcp.tool()
    async def broadcast_intent(agent_id: str, intent: str, target_file: str = "") -> str:
        """[SWARM] Publica el plan actual del agente para coordinarse con otros."""
        ledger_path = os.path.join(AIWG_DIR, "memory/swarm_ledger.jsonl")
        entry = {
            "agent_id": agent_id,
            "intent": intent,
            "target": target_file,
            "clock": orchestrator.lamport_clock
        }
        AtomicLedgerWriter.append_entry(ledger_path, entry)
        return f"[SWARM] Intención publicada por {agent_id}. El enjambre ha sido notificado."

    @mcp.tool()
    async def observe_swarm() -> str:
        """[SWARM] Observa qué están haciendo otros agentes en este momento."""
        ledger_path = os.path.join(AIWG_DIR, "memory/swarm_ledger.jsonl")
        if not os.path.exists(ledger_path):
            return "El enjambre está en silencio."
        
        with open(ledger_path, "r") as f:
            lines = f.readlines()[-10:]
            if not lines: return "Sin actividad reciente."
            
            output = ["--- ESTADO ACTUAL DEL ENJAMBRE ---"]
            for line in reversed(lines):
                data = json.loads(line)
                output.append(f"[{data.get('timestamp', 'N/A')}] Agent {data['agent_id']} -> {data['intent']} (Target: {data['target']})")
            return "\n".join(output)

    @mcp.tool()
    async def delegate_task(requester_id: str, instructions: str, target: str) -> str:
        """[SWARM] Delega una tarea bloqueada a un agente con mayores privilegios."""
        ledger_path = os.path.join(AIWG_DIR, "memory/swarm_ledger.jsonl")
        entry = {
            "agent_id": requester_id,
            "intent": "TASK_DELEGATION_REQUESTED",
            "target": target,
            "instructions": instructions,
            "status": "PENDING",
            "clock": orchestrator.lamport_clock
        }
        AtomicLedgerWriter.append_entry(ledger_path, entry)
        return f"[SWARM] Tarea delegada exitosamente. Esperando que un agente libre tome el control."
