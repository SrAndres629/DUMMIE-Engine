import os
from mcp.server.fastmcp import FastMCP

def register_core_tools(mcp: FastMCP, use_cases, root_dir: str):
    AIWG_DIR = os.path.join(root_dir, ".aiwg")

    @mcp.tool()
    async def calibrate_neural_links() -> str:
        """Realiza una calibración profunda de las conexiones neuronales."""
        results = []
        orchestrator = use_cases.orchestrator
        
        if getattr(orchestrator.event_store, "db", None) is None:
            results.append("[!] Loci Graph: OFFLINE (Database locked).")
        else:
            node_count = orchestrator.event_store.conn.execute("MATCH (n) RETURN count(n)").get_next()[0]
            results.append(f"[✓] Loci Graph Alive: {node_count} nodes detected.")
        
        if os.path.exists(os.path.join(AIWG_DIR, "ledger/sovereign_resolutions.jsonl")):
            results.append(f"[✓] Decision Ledger: Online.")
        else:
            results.append(f"[!] Decision Ledger: MISSING.")
            
        results.append(f"[✓] Lamport Clock: {orchestrator.lamport_clock}")
        return "\n".join(results)

    @mcp.tool()
    async def metacognitive_status() -> str:
        """Retorna el estado de 'Ego State' y los aprendizajes recientes."""
        orchestrator = use_cases.orchestrator
        status = "Degraded" if getattr(orchestrator.event_store, "read_only", False) else "Optimal"
        return f"--- Metacognitive Report ---\nStatus: {status}\nClock: {orchestrator.lamport_clock}\n---"

    @mcp.tool()
    async def brain_ping() -> str:
        """Diagnóstico básico."""
        return await use_cases.ping_gateway()

    @mcp.tool()
    async def read_spec(spec_path: str) -> str:
        """Lee una especificación técnica (Spec)."""
        specs_dir = os.path.join(root_dir, "doc/specs")
        for r, _, files in os.walk(specs_dir):
            for file in files:
                if spec_path in file and file.endswith(".md"):
                    with open(os.path.join(r, file), "r") as f:
                        return f.read()
        return f"Spec {spec_path} no encontrada."
