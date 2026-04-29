import os
import json
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("dummie-mcp.resources")

def register_resources(mcp: FastMCP, get_orchestrator, get_proxy, root_dir: str):
    """Registra todos los recursos en la instancia de FastMCP."""
    
    AIWG_DIR = os.path.join(root_dir, ".aiwg")

    @mcp.resource("brain://identity")
    def get_brain_identity() -> str:
        """Retorna la identidad y arquetipo del sistema."""
        import re
        identity_md_path = os.path.join(root_dir, "IDENTITY.md")
        identity_data = {}
        
        if os.path.exists(identity_md_path):
            try:
                with open(identity_md_path, "r") as f:
                    content = f.read()
                for key in ["Name", "Creature", "Vibe", "Emoji", "Avatar"]:
                    match = re.search(rf"- \*\*.*?{key}.*?\*\*:(.*)", content, re.IGNORECASE)
                    if match:
                        val = match.group(1).strip()
                        if "_(" not in val and val:
                            identity_data[key.lower()] = val
            except Exception as e:
                logger.error(f"Error parsing IDENTITY.md: {e}")
                
        path = os.path.join(AIWG_DIR, "identity.json")
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    json_data = json.load(f)
                if identity_data:
                    json_data.setdefault("personality_profile", {})
                    json_data["personality_profile"]["agent_name"] = identity_data.get("name", "Antigravity")
                    json_data["personality_profile"]["creature"] = identity_data.get("creature", "Ghost")
                    json_data["personality_profile"]["vibe"] = identity_data.get("vibe", "Technical")
                    json_data["personality_profile"]["emoji"] = identity_data.get("emoji", "🌌")
                    json_data["personality_profile"]["avatar"] = identity_data.get("avatar", "")
                return json.dumps(json_data, indent=2)
            except Exception as e:
                logger.error(f"Error reading identity.json: {e}")
                
        if identity_data:
            return json.dumps(identity_data, indent=2)
        return "Identidad desconocida."

    @mcp.resource("brain://dashboard")
    def get_brain_dashboard() -> str:
        """Dashboard de capacidades activas (Anclaje Semántico)."""
        proxy_manager = get_proxy()
        registry = list(proxy_manager.servers.keys())
        return f"--- DASHBOARD ---\nSwarm: {', '.join(registry)}\nUsa 'exec_remote_tool'.\n---"

    @mcp.resource("memory://decisions")
    def get_recent_decisions() -> str:
        """Lee las últimas resoluciones del Ledger."""
        orchestrator = get_orchestrator()
        path = orchestrator.ledger_audit.ledger_path
        if not os.path.exists(path): return "No decisions found."
        with open(path, "r") as f:
            return "".join(f.readlines()[-10:])

    @mcp.resource("memory://timeline")
    def get_memory_timeline() -> str:
        """Stream de eventos inmutables del 4D-TES."""
        orchestrator = get_orchestrator()
        if orchestrator.event_store.conn is None: return "Offline."
        results = orchestrator.event_store.conn.execute(
            "MATCH (m:MemoryNode4D) RETURN m.lamport_t, m.causal_hash, m.intent_i ORDER BY m.lamport_t DESC LIMIT 50"
        )
        events = []
        while results.has_next():
            row = results.get_next()
            events.append(f"T={row[0]} | Hash={row[1]} | Intent={row[2]}")
        return "\n".join(events) if events else "Timeline empty."

    @mcp.resource("memory://loci")
    def get_memory_loci() -> str:
        """Acceso al grafo de relaciones ontológicas."""
        orchestrator = get_orchestrator()
        if orchestrator.event_store.conn is None: return "{}"
        nodes_summary = []
        rels_summary = []
        try:
            node_results = orchestrator.event_store.conn.execute("MATCH (n) RETURN labels(n), count(*)")
            while node_results.has_next(): nodes_summary.append(node_results.get_next())
            rel_results = orchestrator.event_store.conn.execute("MATCH ()-[r]->() RETURN label(r), count(*)")
            while rel_results.has_next(): rels_summary.append(rel_results.get_next())
        except: return "{}"
        return json.dumps({"nodes": nodes_summary, "rels": rels_summary}, indent=2)

    @mcp.resource("brain://health")
    def get_brain_health() -> str:
        """Reporta el estado de salud y modo (MASTER/READER)."""
        orchestrator = get_orchestrator()
        is_read_only = getattr(orchestrator.event_store, "read_only", False)
        return json.dumps({
            "mode": "READER" if is_read_only else "MASTER",
            "kuzu": "Connected" if orchestrator.event_store.db else "Disconnected",
            "clock": orchestrator.lamport_clock
        }, indent=2)

    @mcp.resource("session://context")
    def get_session_context() -> str:
        """Contexto causal filtrado para la sesión activa."""
        if orchestrator.event_store.conn is None: return "Offline."
        # Simplificación para el refactor
        return json.dumps({"session_id": os.environ.get("DUMMIE_SESSION_ID", "GLOBAL")}, indent=2)

    @mcp.resource("specs://active")
    def get_active_specs_list() -> str:
        """Lista de especificaciones activas."""
        specs_list = []
        specs_dir = os.path.join(root_dir, "doc/specs")
        for r, _, files in os.walk(specs_dir):
            for file in files:
                if file.endswith(".md"): specs_list.append(file)
        return "\n".join(specs_list)
