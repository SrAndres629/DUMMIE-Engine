from .pipeline import RoutingResult, RoutingStrategy

LLM_ROUTER_SYSTEM = """Eres un router semántico. Dada una consulta del usuario, devuelve JSON:
{
  "domain": "media_generation|vcs|workspace_io|infrastructure|shell|knowledge|null",
  "gateway": "media|code|infra|shell|knowledge|null",
  "confidence": 0.0-1.0,
  "reasoning": "breve explicación"
}
Solo puedes elegir entre los dominios listados. Si no corresponde a ninguno, usa null."""

class LLMReasoningStrategy:
    name = "llm_reasoning"

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
            from ...models.adapters.ollama_adapter import OllamaAdapter
            from ...models.adapters.base import ModelSpec, ModelType, OntologyClass
            self._adapter = OllamaAdapter(
                ModelSpec(self.model_id, ModelType.LLM, OntologyClass.REASONING)
            )
        await self._adapter.load()

    async def execute(self, query: str) -> RoutingResult:
        await self._ensure_loaded()
        result = await self._adapter.generate_json(LLM_ROUTER_SYSTEM, query)
        domain = result.get("domain")
        gateway = result.get("gateway")
        confidence = result.get("confidence", 0.0)
        if domain and gateway and domain != "null":
            return RoutingResult(match=True, gateway=gateway, domain=domain,
                                 confidence=float(confidence))
        return RoutingResult(match=False, confidence=0.0)
