# Spec: 166_l2_brain_organ_migration_contract
import os
import json
import logging
import asyncio
from typing import Any, Dict, List
from pathlib import Path

logger = logging.getLogger("dummie.brain.diagnostic")

class DiagnosticReporter:
    def __init__(self, daemon: Any):
        self.daemon = daemon
        self.report_path = Path(daemon.ledger_path).parent / "diagnostic_report.json"

    async def run_diagnostic(self) -> Dict[str, Any]:
        logger.info("Running Daemon Diagnostic Suite...")
        
        report = {
            "timestamp": os.getenv("DUMMIE_TIMESTAMP", ""),
            "mode": "DIAGNOSTIC",
            "environment": self._check_env(),
            "layers": await self._check_layers(),
            "metagateway": await self._check_metagateway(),
            "mcp_connectivity": await self._check_mcp(),
            "storage": self._check_storage()
        }
        
        # Write report to disk
        try:
            self.report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            logger.info(f"Diagnostic report written to {self.report_path}")
        except Exception as e:
            logger.error(f"Failed to write diagnostic report: {e}")
            
        return report

    def _check_env(self) -> Dict[str, Any]:
        return {
            "DUMMIE_ROOT": os.getenv("DUMMIE_ROOT", "MISSING"),
            "DUMMIE_LOAD_DOTENV": os.getenv("DUMMIE_LOAD_DOTENV", "0"),
            "PYTHONPATH": os.getenv("PYTHONPATH", ""),
        }

    async def _check_layers(self) -> Dict[str, Any]:
        try:
            from layers.l2_brain.infrastructure.safe_fallbacks import FailClosedAuditor, FailClosedExecutor
        except ImportError:
            try:
                from safe_fallbacks import FailClosedAuditor, FailClosedExecutor
            except ImportError:
                FailClosedAuditor = object
                FailClosedExecutor = object
        
        layers = {}
        
        # Shield Check
        for name, shield in [("S", self.daemon.s_shield), ("E", self.daemon.e_shield), ("L", self.daemon.l_shield)]:
            is_fallback = isinstance(shield, FailClosedAuditor)
            layers[f"shield_{name}"] = {
                "status": "FALLBACK_ACTIVE" if is_fallback else "OK",
                "reason": shield.reason if is_fallback else "Loaded successfully"
            }
            
        # Muscle Check
        is_muscle_fallback = isinstance(self.daemon.muscle, FailClosedExecutor)
        layers["muscle"] = {
            "status": "FALLBACK_ACTIVE" if is_muscle_fallback else "OK",
            "reason": self.daemon.muscle.reason if is_muscle_fallback else "Loaded successfully"
        }
        
        return layers

    async def _check_mcp(self) -> Dict[str, Any]:
        if not self.daemon.mcp_gateway:
            return {"status": "MISSING", "error": "No MCP gateway provided"}
            
        try:
            # Try a simple tool list or heartbeat if available
            # Since we don't want to execute tools, we just check the object
            return {
                "status": "OK",
                "gateway_type": type(self.daemon.mcp_gateway).__name__
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def _check_storage(self) -> Dict[str, Any]:
        ledger = Path(self.daemon.ledger_path)
        return {
            "ledger_path": str(ledger),
            "exists": ledger.exists(),
            "writable": os.access(ledger.parent, os.W_OK) if ledger.parent.exists() else False
        }

    async def _check_metagateway(self) -> Dict[str, Any]:
        """Check Meta-Gateway status and Metacognitive Pipeline."""
        status = getattr(self.daemon, "metacognition_status", "MISSING")
        error = getattr(self.daemon, "metacognition_error", "")
        
        hooks = []
        if self.daemon.metacognition and hasattr(self.daemon.metacognition, "input_hooks"):
            hooks = [type(h).__name__ for h in self.daemon.metacognition.input_hooks]

        return {
            "status": status,
            "metacognition_status": status,
            "metacognition_error": error,
            "enabled_hooks": hooks,
            "cognitive_preflight_enabled": self.daemon.diagnostic_mode or os.getenv("DUMMIE_COGNITIVE_PREFLIGHT") == "1",
            "local_reasoning_gateway_available": hasattr(self.daemon, "mcp_gateway") and self.daemon.mcp_gateway is not None
        }
