from routing.pipeline import RoutingResult, RoutingStrategy

GATEWAYS_INFO = """- media (8081): muapi, mcp-comfyui, cloudflare — imágenes, video, audio
- code (8082): github, git, filesystem — repos, archivos, workspace
- infra (8083): docker, vercel — contenedores, deploy, cloud
- knowledge (8084): sqlite, sequentialthinking — DBs, memoria, razonamiento
- shell (8085): shell, mcp-bash, browser-use — comandos, terminal, web"""


class CoTReasoningStrategy:
    name = "cot_reasoning"

    def __init__(self, registry=None, model_id: str = "gemma3:1b", context_engine=None):
        self.registry = registry
        self.model_id = model_id
        self._adapter = None
        self._enricher = None

    async def _get_enricher(self):
        if self._enricher is None:
            from context.cot_enricher import CoTEnricher
            from context.dimensions.temporal import TemporalDimension
            from context.dimensions.spatial import SpatialDimension
            from context.dimensions.semantic import SemanticDimension
            from context.dimensions.relational import RelationalDimension
            from context.dimensions.episodic import EpisodicDimension
            from context.dimensions.instrumental import InstrumentalDimension

            self._enricher = CoTEnricher()
            self._enricher.register_dimension(TemporalDimension())
            self._enricher.register_dimension(SpatialDimension())
            self._enricher.register_dimension(SemanticDimension())
            self._enricher.register_dimension(RelationalDimension())
            self._enricher.register_dimension(EpisodicDimension())

            try:
                from meta_router import MetaRouter

                mr = MetaRouter()
                self._enricher.register_dimension(InstrumentalDimension(meta_router=mr))
            except Exception:
                self._enricher.register_dimension(InstrumentalDimension())

        return self._enricher

    async def _ensure_loaded(self):
        if self._adapter is not None:
            return
        if self.registry:
            self._adapter = self.registry.get_or_create(self.model_id)
        else:
            from models.adapters.ollama_adapter import OllamaAdapter
            from models.adapters.base import ModelSpec, ModelType, OntologyClass

            self._adapter = OllamaAdapter(
                ModelSpec(self.model_id, ModelType.LLM, OntologyClass.REASONING)
            )
        await self._adapter.load()

    async def execute(self, query: str) -> RoutingResult:
        await self._ensure_loaded()
        enricher = await self._get_enricher()
        prompt = await enricher.build_cot_prompt(
            query, active_dims=["temporal", "spatial", "relational", "instrumental"]
        )
        system = f"""[SISTEMA]: Eres un router con Chain of Thought profundo.

Gateways:
{GATEWAYS_INFO}

Reglas:
1. Piensa paso a paso antes de decidir
2. Si la consulta es ambigua, pide clarificación
3. Usa el contexto 6D para mejorar tu decisión
4. Si necesitas conocimiento del Obsidian vault, indícalo
5. Devuelve siempre JSON válido

[CONTEXTO 6D]:
{prompt}

Responde SOLO con JSON."""

        result = await self._adapter.generate_json(system, query, temperature=0.2)
        reasoning = result.get("reasoning", "")
        domain = result.get("domain")
        gateway = result.get("gateway")
        confidence = result.get("confidence", 0.0)
        needs_clarification = result.get("needs_clarification", False)

        if domain and gateway and domain != "null":
            return RoutingResult(
                match=True,
                gateway=gateway,
                domain=domain,
                action="cot_resolved",
                confidence=float(confidence),
                query=query,
            )
        if needs_clarification:
            return RoutingResult(
                match=False,
                confidence=float(confidence),
                query=query,
            )

        return RoutingResult(match=False, confidence=0.0, query=query)
