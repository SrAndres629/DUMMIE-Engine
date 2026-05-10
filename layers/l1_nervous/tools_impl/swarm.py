import os
import json
from mcp.server.fastmcp import FastMCP
from utils import AtomicLedgerWriter
from runtime_paths import iter_dummied_socket_candidates

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
    @mcp.tool()
    async def spawn_agent(goal: str, manifest_path: str = "", id: str = "") -> str:
        """[SWARM] Crea e inyecta un nuevo agente/enjambre en el motor L0."""
        import socket
        import yaml
        if not manifest_path:
            # Manifiesto por defecto si no se provee uno
            manifest = {
                "version": "2.0",
                "swarm_id": f"spawned_{id}" if id else "dynamic_spawn",
                "meta": {"goal": goal, "max_iterations": 5},
                "graph": {
                    "nodes": [{"id": "init", "type": "GENERIC", "config": {"goal": goal}}],
                    "edges": []
                }
            }
        else:
            if not os.path.isabs(manifest_path):
                manifest_path = os.path.join(root_dir, manifest_path)
            
            if not os.path.exists(manifest_path):
                return f"Error: Manifiesto no encontrado en {manifest_path}"
                
            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f)

        cmd = {
            "type": "SPAWN_SWARM",
            "goal": goal,
            "id": id,
            "manifest": manifest
        }

        errors = []
        for socket_path in iter_dummied_socket_candidates(root_dir):
            try:
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.connect(str(socket_path))
                client.sendall(json.dumps(cmd).encode())
                response = client.recv(4096).decode()
                client.close()
                return f"[SWARM] Agente inyectado exitosamente: {response}"
            except Exception as e:
                errors.append(f"{socket_path}: {e}")

        return "Error al conectar con el daemon L0 (¿está encendido?): " + " | ".join(errors)
