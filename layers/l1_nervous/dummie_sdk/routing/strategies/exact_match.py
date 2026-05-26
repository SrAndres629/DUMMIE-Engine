import re
from typing import Optional
from dummie_sdk.routing.types import RoutingResult
from dummie_sdk.routing.strategies.base import BaseRoutingStrategy


class ExactMatchStrategy(BaseRoutingStrategy):
    name = "exact_match"

    INTENT_MAP = [
        (
            r"imagen|image|generar.*imagen|generar.*foto|dibujar|ilustraci",
            "media_generation",
            "image",
        ),
        (r"video|generar.*video|crear.*video|animacion", "media_generation", "video"),
        (
            r"audio|musica|música|generar.*audio|generar.*sonido|cancion",
            "media_generation",
            "audio",
        ),
        (r"git|commit|push|pull|branch|repositorio|repo|merge|clone", "vcs", "git"),
        (
            r"archivo|file|leer|escribir|read|write|filesystem|directorio|folder",
            "workspace_io",
            "file",
        ),
        (
            r"docker|contenedor|container|imagen.*docker|compose",
            "infrastructure",
            "docker",
        ),
        (
            r"vercel|deploy|desplegar|hosting|dominio|domain|deployment",
            "infrastructure",
            "deploy",
        ),
        (
            r"sql|query|base.*datos|database|consulta|memoria|knowledge|select|insert",
            "knowledge",
            "query",
        ),
        (
            r"n8n|workflow|workflows|webhook|webhooks|automatiza|automatizar|automation",
            "automation",
            "workflow",
        ),
        (r"shell|terminal|comando|command|ejecutar|run|bash|zsh", "shell", "shell"),
        (
            r"navegador|browser|web|pagina|test.*web|chrome|firefox|navegar",
            "shell",
            "browser",
        ),
        (
            r"razonar|pensar|planificar|analizar|think|reason|plan|reflexionar",
            "knowledge",
            "reason",
        ),
    ]

    GATEWAY_MAP = {
        "media_generation": "media",
        "image": "media",
        "video": "media",
        "audio": "media",
        "vcs": "code",
        "workspace_io": "code",
        "infrastructure": "infra",
        "deployment": "infra",
        "knowledge": "knowledge",
        "memory": "knowledge",
        "reasoning": "knowledge",
        "shell": "shell",
        "automation": "shell",
        "browser": "shell",
    }

    async def execute(self, query: str) -> RoutingResult:
        q = query.lower().strip()
        for pattern, domain, action in self.INTENT_MAP:
            if re.search(pattern, q):
                return RoutingResult(
                    match=True,
                    domain=domain,
                    action=action,
                    gateway=self.GATEWAY_MAP.get(domain, ""),
                    confidence=1.0,
                    strategy=self.name,
                )
        return RoutingResult(match=False, confidence=0.0, strategy=self.name)
