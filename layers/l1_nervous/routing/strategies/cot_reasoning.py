from routing.pipeline import RoutingResult, RoutingStrategy

COT_SYSTEM = """Eres un router con Chain of Thought. Dada una consulta, piensa paso a paso y decide a qué gateway enrutarla.

Gateways disponibles:
- media: generación de imágenes, videos, audio
- code: git, archivos, repositorios
- infra: docker, vercel, infraestructura cloud
- knowledge: SQL, bases de datos, memoria, razonamiento
- shell: comandos shell, terminal, navegador web

Devuelve SOLO JSON:
{
  "reasoning": "paso a paso tu razonamiento",
  "domain": "media_generation|vcs|workspace_io|infrastructure|shell|knowledge",
  "gateway": "media|code|infra|knowledge|shell",
  "confidence": 0.0-1.0
}
"""


class CoTReasoningStrategy:
    name = "cot_reasoning"

    def __init__(self, registry=None, model_id: str = "gemma3:1b"):
        self.registry = registry
        self.model_id = model_id
        self._adapter = None

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
        result = await self._adapter.generate_json(COT_SYSTEM, query)
        reasoning = result.get("reasoning", "")
        domain = result.get("domain")
        gateway = result.get("gateway")
        confidence = result.get("confidence", 0.0)
        if domain and gateway and domain != "null":
            return RoutingResult(
                match=True,
                gateway=gateway,
                domain=domain,
                action="cot_resolved",
                confidence=float(confidence),
                query=query,
            )
        return RoutingResult(match=False, confidence=0.0, query=query)
