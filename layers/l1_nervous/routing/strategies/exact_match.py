import re
from routing.pipeline import RoutingResult, RoutingStrategy

DOMAIN_MAP = {
    "imagen|image|generar.*imagen|generar.*foto|generar.*img|dibujar|ilustraci": ("media_generation", "image", "media"),
    "video|generar.*video|crear.*video|generar.*clip|animacion": ("media_generation", "video", "media"),
    "audio|musica|música|generar.*audio|generar.*sonido|cancion": ("media_generation", "audio", "media"),
    "git|commit|push|pull|branch|repositorio|repo|merge|clone": ("vcs", "git", "code"),
    "archivo|file|leer|escribir|read|write|filesystem|directorio|folder": ("workspace_io", "file", "code"),
    "docker|contenedor|container|imagen.*docker|compose": ("infrastructure", "docker", "infra"),
    "vercel|deploy|desplegar|hosting|dominio|domain|deployment": ("infrastructure", "deploy", "infra"),
    "sql|query|base.*datos|database|consulta|memoria|knowledge|select|insert": ("knowledge", "query", "knowledge"),
    "shell|terminal|comando|command|ejecutar|run|bash|zsh": ("shell", "shell", "shell"),
    "navegador|browser|web|pagina|test.*web|chrome|firefox|navegar": ("shell", "browser", "shell"),
    "razonar|pensar|planificar|analizar|think|reason|plan|reflexionar": ("knowledge", "reason", "knowledge"),
}

class ExactMatchStrategy:
    name = "exact_match"

    async def execute(self, query: str) -> RoutingResult:
        q = query.lower().strip()
        for pattern, (domain, action, gateway) in DOMAIN_MAP.items():
            if re.search(pattern, q):
                return RoutingResult(
                    match=True, gateway=gateway, domain=domain,
                    action=action, confidence=1.0,
                )
        return RoutingResult(match=False, confidence=0.0)
