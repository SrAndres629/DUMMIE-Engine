import yaml
import logging
import json
import fcntl
from typing import List, Dict, Any
from pathlib import Path

# Nota: 'edge' debe estar en el PYTHONPATH para resolver esta importación en tiempo de ejecución
try:
    from edge import ToolDiscovery
except ImportError:
    logger = logging.getLogger("skill-binder")
    logger.warning("L4_Edge not found in path. ToolDiscovery will be limited.")

logger = logging.getLogger("skill-binder")

class SkillBinder:
    """
    Gestiona el enlace (binding) entre Skills YAML y Herramientas MCP.
    Utiliza L4_Edge como sensor de capacidades físicas.
    """
    def __init__(self, skills_dir: str, mcp_gateway: Any):
        self.skills_dir = Path(skills_dir)
        self.mcp_gateway = mcp_gateway
        try:
            self.discovery = ToolDiscovery(mcp_gateway)
        except NameError:
            self.discovery = None
            
        self.agent_profiles: Dict[str, Dict[str, Any]] = {}

    def load_all_skills(self):
        """Carga perfiles de agentes desde archivos YAML."""
        for yaml_file in self.skills_dir.glob("*.yaml"):
            try:
                with open(yaml_file, "r") as f:
                    profile = yaml.safe_load(f)
                    agent_name = profile.get("name")
                    self.agent_profiles[agent_name] = profile
                    logger.info(f"Skill profile cached: {agent_name}")
            except Exception as e:
                logger.error(f"Failed to load skill YAML {yaml_file.name}: {e}")

    async def validate_all_contracts(self):
        """Valida todos los perfiles contra el sensor de L4."""
        for name, profile in self.agent_profiles.items():
            await self._validate_contract(profile)

    async def _validate_contract(self, profile: Dict[str, Any]):
        """Valida capacidades físicas reales."""
        if not self.discovery:
            logger.error("Cannot validate contract: L4 Sensor offline.")
            return

        try:
            inventory = await self.discovery.get_available_capabilities()
            required = profile.get("capabilities", [])
            for cap in required:
                if cap.lower() not in [c.lower() for c in inventory]:
                    logger.critical(f"Contract Mismatch: {cap} missing for {profile['name']}")
                    raise RuntimeError(f"Missing capability: {cap}")
        except Exception as e:
            logger.error(f"Validation failed for {profile['name']}: {e}")
            raise
