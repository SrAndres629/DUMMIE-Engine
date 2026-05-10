import os
from mcp.server.fastmcp import FastMCP

__spec_id__ = "DE-V2-L4-18"

def register_core_tools(mcp: FastMCP, use_cases, root_dir: str):
    AIWG_DIR = os.path.join(root_dir, ".aiwg")

    @mcp.tool()
    async def calibrate_neural_links() -> str:
        """Realiza una calibración profunda de las conexiones neuronales."""
        results = []
        orchestrator = use_cases.orchestrator
        
        if getattr(orchestrator.event_store, "read_only", False) or getattr(orchestrator.event_store, "conn", None) is None:
            results.append("[!] Loci Graph: OFFLINE (Database locked or stub mode).")
        else:
            try:
                # Kuzu python API returns a QueryResult, using get_next() or iterating
                res = orchestrator.event_store.conn.execute("MATCH (n) RETURN count(n)")
                node_count = 0
                if hasattr(res, "get_next"):
                    node_count = res.get_next()[0]
                elif hasattr(res, "get_next_row"):
                    node_count = res.get_next_row()[0]
                elif hasattr(res, "has_next"):
                    while res.has_next():
                        node_count = res.get_next()[0]
                else:
                    # Kuzu 0.6+ query result iteration
                    for row in res:
                        node_count = row[0]
                results.append(f"[✓] Loci Graph Alive: {node_count} nodes detected (Native Mode).")
            except Exception as e:
                results.append(f"[!] Loci Graph: ERROR ({e})")
        
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
    async def operational_truth_report(format: str = "text", include_slow: bool = False) -> str:
        """[TRUTH] Reporta el estado operacional real de DUMMIE Engine."""
        import json as _json
        import sys as _sys

        l2_path = os.path.join(root_dir, "layers", "l2_brain")
        if l2_path not in _sys.path:
            _sys.path.insert(0, l2_path)

        from operational_truth_collectors import collect_truth

        report = collect_truth(root_dir, include_slow=include_slow)
        if format == "json":
            return _json.dumps(report.to_dict(), indent=2)

        lines = [
            "=== DUMMIE OPERATIONAL TRUTH ===",
            f"Repo: {report.repo_root}",
            f"Summary: {report.summary()}",
        ]
        for check in report.checks:
            evidence = "; ".join(check.evidence) if check.evidence else check.error
            lines.append(f"- [{check.status.value}] {check.layer} {check.name}: {evidence}")
            if check.next_repair:
                lines.append(f"  next: {check.next_repair}")
        return "\n".join(lines)

    @mcp.tool()
    async def read_spec(spec_id: str) -> str:
        """
        Lee una especificación técnica (Spec) por su ID.
        
        El spec_id es un identificador parcial que se busca en los nombres de archivo
        dentro de doc/specs/. No acepta rutas ni caracteres de path traversal.
        
        Retorna el contenido del spec, o un JSON de error si no se encuentra.
        """
        import json as _json

        # [SECURITY] Validar que spec_id no contenga path traversal
        forbidden_chars = ["..", "/", "\\", "\x00"]
        for char in forbidden_chars:
            if char in spec_id:
                return _json.dumps({
                    "error": "SPEC_ID_INVALID",
                    "spec_id": spec_id,
                    "reason": f"spec_id contains forbidden character: {repr(char)}"
                })

        if not spec_id.strip():
            return _json.dumps({
                "error": "SPEC_ID_EMPTY",
                "spec_id": spec_id,
                "reason": "spec_id cannot be empty"
            })

        specs_dir = os.path.join(root_dir, "doc/specs")
        if not os.path.isdir(specs_dir):
            return _json.dumps({
                "error": "SPECS_DIR_NOT_FOUND",
                "specs_dir": specs_dir,
            })

        valid_extensions = (".md", ".yaml", ".yml")
        for r, _, files in os.walk(specs_dir):
            # [SECURITY] Asegurar que no escapamos de specs_dir
            real_r = os.path.realpath(r)
            real_specs = os.path.realpath(specs_dir)
            if not real_r.startswith(real_specs):
                continue

            for file in files:
                if spec_id in file and file.endswith(valid_extensions):
                    filepath = os.path.join(r, file)
                    # Double-check realpath
                    if not os.path.realpath(filepath).startswith(real_specs):
                        continue
                    with open(filepath, "r") as f:
                        content = f.read()

                    # Intentar parsear frontmatter YAML si existe
                    metadata = {}
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            try:
                                import yaml
                                metadata = yaml.safe_load(parts[1]) or {}
                            except Exception:
                                pass  # Si no se puede parsear, se ignora

                    result = {
                        "spec_id": spec_id,
                        "file": file,
                        "content": content,
                    }
                    if metadata:
                        result["metadata"] = metadata
                    return _json.dumps(result)

        return _json.dumps({
            "error": "SPEC_NOT_FOUND",
            "spec_id": spec_id,
            "searched_dir": specs_dir,
        })
