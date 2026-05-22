import json, re
from pathlib import Path
from embeddings import EmbeddingRouter

CONFIG_PATH = Path(__file__).parent / "configs" / "meta_router_assignments.json"


class MetaRouter:
    def __init__(self):
        with open(CONFIG_PATH) as f:
            self.assignments = json.load(f)
        self.embedding_router = EmbeddingRouter()
        self._build_index()

    def _build_index(self):
        self._domain_to_gateway = {}
        for gw_name, gw_cfg in self.assignments["gateways"].items():
            for domain in gw_cfg["domains"]:
                self._domain_to_gateway[domain] = gw_name

    def route(self, query: str) -> dict:
        query_lower = query.lower().strip()
        domain, action = self._parse_intent(query_lower)
        if domain:
            confidence = 1.0
        else:
            best = self.embedding_router.best_domain(query)
            domain = best[0] if best else None
            confidence = best[1] if best else 0.0

        if not domain:
            return {
                "match": False,
                "domain": None,
                "confidence": 0.0,
                "message": "Could not determine domain from query",
            }

        gw_name = self._domain_to_gateway.get(domain)
        if not gw_name:
            return {
                "match": False,
                "domain": domain,
                "confidence": confidence,
                "message": f"No gateway configured for domain '{domain}'",
            }

        gw_cfg = self.assignments["gateways"][gw_name]
        return {
            "match": True,
            "domain": domain,
            "action": action,
            "gateway": gw_name,
            "port": gw_cfg["port"],
            "confidence": confidence,
            "servers": list(gw_cfg["servers"].keys()),
        }

    def _parse_intent(self, query: str):
        intent_map = [
            (
                "imagen|image|generar.*imagen|generar.*foto|generar.*img|dibujar|ilustraci",
                "media_generation",
                "image",
            ),
            (
                "video|generar.*video|crear.*video|generar.*clip|animacion",
                "media_generation",
                "video",
            ),
            (
                "audio|musica|música|generar.*audio|generar.*sonido|cancion",
                "media_generation",
                "audio",
            ),
            ("git|commit|push|pull|branch|repositorio|repo|merge|clone", "vcs", "git"),
            (
                "archivo|file|leer|escribir|read|write|filesystem|directorio|folder",
                "workspace_io",
                "file",
            ),
            (
                "docker|contenedor|container|imagen.*docker|compose",
                "infrastructure",
                "docker",
            ),
            (
                "vercel|deploy|desplegar|hosting|dominio|domain|deployment",
                "infrastructure",
                "deploy",
            ),
            (
                "sql|query|base.*datos|database|consulta|memoria|knowledge|select|insert",
                "knowledge",
                "query",
            ),
            ("shell|terminal|comando|command|ejecutar|run|bash|zsh", "shell", "shell"),
            (
                "navegador|browser|web|pagina|test.*web|chrome|firefox|navegar",
                "shell",
                "browser",
            ),
            (
                "razonar|pensar|planificar|analizar|think|reason|plan|reflexionar",
                "knowledge",
                "reason",
            ),
        ]
        for pattern, dom, act in intent_map:
            if re.search(pattern, query):
                return dom, act
        return None, None

    def list_all_capabilities(self) -> list[dict]:
        caps = []
        for gw_name, gw_cfg in self.assignments["gateways"].items():
            for srv_name, srv_cfg in gw_cfg["servers"].items():
                caps.append(
                    {
                        "gateway": gw_name,
                        "server": srv_name,
                        "port": gw_cfg["port"],
                        "tools": srv_cfg.get("tools", ["*"]),
                    }
                )
        return caps
