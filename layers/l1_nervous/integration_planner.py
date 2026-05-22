import json
import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger("dummie-mcp.integration-planner")


@dataclass
class IntegrationPlan:
    name: str
    source_url: str
    description: str
    language: str
    stars: int
    integration_type: str = "mcp_wrapper"
    rationale: str = ""
    steps: List[str] = field(default_factory=list)
    risk: str = "medium"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "source_url": self.source_url,
            "description": self.description,
            "language": self.language,
            "stars": self.stars,
            "integration_type": self.integration_type,
            "rationale": self.rationale,
            "steps": self.steps,
            "risk": self.risk,
        }


class IntegrationPlanner:
    def generate_plan(self, search_result: dict) -> Optional[IntegrationPlan]:
        results = search_result.get("results", [])
        if not results:
            return None

        best = results[0]
        if best.get("stars", 0) < 10:
            logger.info(
                "Repo '%s' tiene solo %s estrellas, muy pequeño",
                best.get("name", "?"),
                best.get("stars", 0),
            )
            if len(results) > 1:
                best = results[1]
            else:
                return None

        plan = IntegrationPlan(
            name=self._extract_name(best.get("name", "unknown")),
            source_url=best.get("url", ""),
            description=best.get("description", ""),
            language=best.get("language", "unknown"),
            stars=best.get("stars", 0),
            rationale=(
                f"Repo con {best.get('stars', 0)} estrellas en GitHub. "
                f"Lenguaje: {best.get('language', 'N/A')}. "
                f"Actualizado: {best.get('updated_at', 'N/A')}."
            ),
            steps=self._build_steps(best),
            risk=self._assess_risk(best),
        )
        return plan

    def _extract_name(self, full_name: str) -> str:
        return full_name.split("/")[-1] if "/" in full_name else full_name

    def _build_steps(self, repo: dict) -> List[str]:
        name = self._extract_name(repo.get("name", ""))
        url = repo.get("url", "")

        steps = [
            f"1. Clonar/instalar '{name}' desde {url}",
            f"2. Verificar dependencias y compatibilidad con MCP protocolo",
            f"3. Crear wrapper MCP stdio en scripts/ si es necesario",
            f"4. Registrar en dummie_gateway_config.json con profile y capability_class",
            f"5. Registrar en .aiwg/registry/mcp_registry.json como canonical",
            f"6. Ejecutar verificacion: ping -> initialize -> tool call",
            f"7. Registrar en ledger: sovereign_resolutions.jsonl",
        ]

        if repo.get("language") == "python":
            steps.append(
                "2.1 Asegurar que las dependencias esten en el .venv raiz via uv"
            )
        elif repo.get("language") in ("javascript", "typescript"):
            steps.append("2.1 Asegurar que node_modules este disponible o usar npx/uvx")

        return steps

    def _assess_risk(self, repo: dict) -> str:
        stars = repo.get("stars", 0)
        if stars >= 1000:
            return "low"
        elif stars >= 100:
            return "medium"
        else:
            return "high"
