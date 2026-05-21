import os
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger("brain.auto_evolution")

class CognitiveAutoEvolver:
    """
    [L2_BRAIN] Orquestador de Autoevolución.
    Maneja los bucles de Git, Observabilidad y Generación de PRs.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.socraticode = None # Injected by orchestrator
        from expansion_policy import ExpansionPolicy
        self.policy = ExpansionPolicy(workspace_root)
        self.feedback_loop = None # Injected by orchestrator

    def collect_performance_metrics(self) -> Dict[str, Any]:
        """
        Recopila métricas reales si el feedback loop está disponible, de lo contrario simula.
        """
        logger.info("Collecting real-time performance metrics...")
        if self.feedback_loop and self.feedback_loop.snapshots:
            last_snapshot = self.feedback_loop.snapshots[-1]
            import dataclasses
            return dataclasses.asdict(last_snapshot)
            
        return {
            "status": "OPTIMAL",
            "bottlenecks": [],
            "active_routines": 12,
            "simulated": True
        }

    def execute_git_push_action(self, branch_name: str, commit_message: str) -> bool:
        """
        Ejecuta operaciones Git locales (Commit & Push) asumiendo levantamiento de Sandbox.
        """
        logger.info(f"Initiating evolutionary commit on branch: {branch_name}")
        try:
            # Comandos secuenciales
            commands = [
                ["git", "checkout", "-b", branch_name],
                ["git", "add", "."],
                ["git", "commit", "-m", commit_message],
                ["git", "push", "origin", branch_name]
            ]
            for cmd in commands:
                result = subprocess.run(
                    cmd,
                    cwd=self.workspace_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode != 0:
                    logger.error(f"Git command failed: {' '.join(cmd)} -> {result.stderr.strip()}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Git execution critical failure: {e}")
            return False

    def generate_pull_request(self, title: str, body: str) -> str:
        """
        Genera la estructura descriptiva para un Pull Request evolutivo.
        """
        logger.info(f"Formulating PR: {title}")
        pr_template = f"""
# 🧠 [AUTO-EVOLUTION] {title}

## Rationale
{body}

## Verification
- Automated Test Coverage: Pending
- Blast Radius: Calculated via AST Blast Radius Indexer.
"""
    async def analyze_failure(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        [WAVE 6] Analiza un fallo sistémico para encontrar la causa raíz.
        """
        msg = error_context.get("message", "").lower()
        stack = error_context.get("stack_trace", "")
        
        affected_files = []
        import re
        # Extraer archivos del stack trace
        file_matches = re.findall(r"File ['\"](.+?)['\"]", stack)
        for f in file_matches:
            if f not in affected_files:
                affected_files.append(f)
        
        root_cause = "Unknown structural anomaly"
        if "no module named" in msg:
            root_cause = f"Missing dependency or incorrect PYTHONPATH: {msg}"
        elif "connection refused" in msg or "not established" in msg:
            root_cause = "Infrastructure connectivity failure (Service Down)"
        elif "locked" in msg:
            root_cause = "Resource contention (File Lock/Race Condition)"
            
        # [WAVE 8] Análisis de Impacto vía Socraticode
        blast_radius = []
        if self.socraticode:
            try:
                for f in affected_files:
                    impact = await self.socraticode.codebase_impact(target=f)
                    if isinstance(impact, list):
                        blast_radius.extend([item.get('filePath') for item in impact if item.get('filePath')])
            except Exception as e:
                logger.warning(f"Socraticode impact analysis failed: {e}")

        logger.info(f"Auto-Evolution: Analysis complete. Root Cause: {root_cause}")
        return {
            "root_cause": root_cause,
            "affected_files": affected_files,
            "blast_radius": list(set(blast_radius)),
            "severity": "CRITICAL" if "import" in msg or "connection" in msg else "ROUTINE"
        }

    async def propose_fix(self, analysis: Dict[str, Any], daemon: Any) -> str:
        """
        Usa el DummieDaemon para razonar una solución.
        """
        prompt = (
            f"Como DUMMIE Engine, analiza este fallo y propone una corrección en formato de parche:\n"
            f"Causa Raíz: {analysis['root_cause']}\n"
            f"Archivos Afectados: {analysis['affected_files']}\n"
            f"Por favor, devuelve solo el razonamiento técnico y el pseudocódigo del parche."
        )
        return await daemon.reason_with_tiers(prompt, concept="self_healing")

    async def self_program(self, mission: str, daemon: Any) -> Dict[str, Any]:
        """
        [WAVE 7] DUMMIE escribe su propio código para cumplir una misión.
        """
        logger.info(f"Self-Programming: Starting mission '{mission}'")
        
        prompt = (
            f"Como DUMMIE Engine (Entidad Soberana), tu misión es programar un nuevo módulo funcional para cumplir esto: {mission}\n"
            "Reglas:\n"
            "1. El código debe ser Python puro, altamente tipado y modular.\n"
            "2. Incluye docstrings detallados.\n"
            "3. Devuelve el código dentro de un bloque ```python\n"
            "4. No incluyas explicaciones innecesarias fuera del bloque de código."
        )
        
        generated_code_raw = await daemon.reason_with_tiers(prompt, concept="self_programming")
        
        # Extraer el bloque de código
        import re
        code_match = re.search(r"```python\n(.*?)```", generated_code_raw, re.DOTALL)
        if not code_match:
            return {"success": False, "error": "No valid python block found in reasoning output"}
            
        code = code_match.group(1)
        
        # [WAVE 9] Resolución Inteligente de Rutas vía Policy
        suggested_name = mission.lower().replace(" ", "_")[:25] + ".py"
        component_type = self.policy.categorize_mission(mission)
        target_path = self.policy.resolve_path(component_type, suggested_name)
        
        # Escribir y validar sintaxis
        try:
            with open(target_path, "w") as f:
                f.write(code)
            
            # Syntax check
            compile(code, target_path, 'exec')
            # [WAVE 8] Indexar nuevo código en Socraticode
            if self.socraticode:
                await self.socraticode.codebase_update(projectPath=self.workspace_root)
                
            return {"success": True, "file_path": target_path, "code_preview": code[:200] + "..."}
        except Exception as e:
            logger.error(f"Self-Programming: Validation failed for {target_path}: {e}")
            if os.path.exists(target_path):
                os.remove(target_path)
            return {"success": False, "error": str(e)}

    async def autonomous_mcp_ingestion(self, server_name: str, command: str, args: list, env: dict = None):
        """
        [WAVE 9] DUMMIE ingiere una nueva herramienta MCP dinámicamente.
        """
        config_path = os.path.join(self.workspace_root, "dummie_gateway_config.json")
        try:
            import json
            with open(config_path, "r") as f:
                config = json.load(f)
            
            config["mcpServers"][server_name] = {
                "command": command,
                "args": args,
                "env": env or {},
                "disabled": False
            }
            
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Autonomous Ingestion: MCP Server '{server_name}' added to gateway.")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest MCP server {server_name}: {e}")
            return False


