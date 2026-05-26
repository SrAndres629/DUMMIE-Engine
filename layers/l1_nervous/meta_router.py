import json, re, asyncio
from pathlib import Path
from typing import Optional
from dummie_sdk.routing.delegation import DelegationEngine, DelegationRequest

CONFIG_PATH = Path(__file__).parent / "configs" / "meta_router_assignments.json"


class MetaRouter:
    def __init__(
        self,
        use_pipeline: bool = False,
        delegation_engine: Optional[DelegationEngine] = None,
    ):
        with open(CONFIG_PATH) as f:
            self.assignments = json.load(f)
        self._use_pipeline = use_pipeline
        self._pipeline = None
        self._delegation = delegation_engine or DelegationEngine()
        self._build_index()

    def _build_index(self):
        self._domain_to_gateway = {}
        for gw_name, gw_cfg in self.assignments["gateways"].items():
            for domain in gw_cfg["domains"]:
                self._domain_to_gateway[domain] = gw_name

    async def _get_pipeline(self):
        if self._pipeline is None:
            from dummie_sdk.routing.pipeline import RoutingPipeline
            from dummie_sdk.routing.strategies.exact_match import ExactMatchStrategy
            from dummie_sdk.routing.strategies.embedding_match import (
                EmbeddingMatchStrategy,
            )
            from dummie_sdk.routing.strategies.cross_encoder_rerank import (
                CrossEncoderRerankStrategy,
            )
            from dummie_sdk.routing.strategies.llm_reasoning import LLMReasoningStrategy
            from dummie_sdk.models.model_registry import ModelRegistry

            registry = ModelRegistry()
            self._pipeline = RoutingPipeline(
                [
                    ExactMatchStrategy(),
                    EmbeddingMatchStrategy(registry=registry),
                    CrossEncoderRerankStrategy(registry=registry),
                    LLMReasoningStrategy(registry=registry),
                ],
                threshold=0.5,
            )
        return self._pipeline

    async def route(self, query: str) -> dict:
        route = await self._resolve_route(query)
        if not route.get("match"):
            return route

        delegation_req = DelegationRequest.from_route(route)
        delegation = await self._delegation.decide(delegation_req)
        route["delegation"] = {
            "location": delegation.location.value,
            "server": delegation.server,
            "reason": delegation.reason,
            "confidence": delegation.confidence,
        }
        return route

    async def _resolve_route(self, query: str) -> dict:
        if self._use_pipeline:
            pipeline = await self._get_pipeline()
            result = await pipeline.route(query)
            if result.match:
                gw_name = result.gateway
                gw_cfg = self.assignments["gateways"].get(gw_name)
                if gw_cfg:
                    return {
                        "match": True,
                        "domain": result.domain,
                        "action": result.action,
                        "gateway": gw_name,
                        "port": gw_cfg["port"],
                        "confidence": result.confidence,
                        "strategy": result.strategy,
                        "latency_ms": result.latency_ms,
                        "servers": list(gw_cfg["servers"].keys()),
                    }
            return {
                "match": False,
                "domain": None,
                "confidence": result.confidence,
                "message": "Could not determine domain from query",
            }

        query_lower = query.lower().strip()
        domain, action = self._parse_intent(query_lower)
        if domain:
            confidence = 1.0
        else:
            from dummie_sdk.routing.strategies.embedding_match import (
                EmbeddingMatchStrategy,
            )

            strat = EmbeddingMatchStrategy()
            result = await strat.execute(query)
            domain = result.domain if result.match else None
            confidence = result.confidence if result.match else 0.0

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
