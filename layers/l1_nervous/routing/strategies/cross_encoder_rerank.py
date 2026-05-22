from routing.pipeline import RoutingResult, RoutingStrategy

class CrossEncoderRerankStrategy:
    name = "cross_encoder_rerank"

    def __init__(self, registry=None):
        self.registry = registry
        self._adapter = None
        self._candidates = [
            ("media", "media_generation", "generación de imágenes y videos"),
            ("code", "vcs", "control de versiones con git"),
            ("code", "workspace_io", "lectura y escritura de archivos"),
            ("infra", "infrastructure", "gestión de infraestructura y contenedores"),
            ("shell", "shell", "ejecución de comandos shell"),
            ("knowledge", "knowledge", "consultas SQL y base de datos"),
        ]

    async def _ensure_loaded(self):
        if self._adapter is not None:
            return
        model_id = "cross-encoder/ms-marco-MiniLM-L-2-v2"
        if self.registry:
            self._adapter = self.registry.get_or_create(model_id)
        else:
            from ...models.adapters.cross_encoder_adapter import CrossEncoderAdapter
            from ...models.adapters.base import ModelSpec, ModelType, OntologyClass
            self._adapter = CrossEncoderAdapter(
                ModelSpec(model_id, ModelType.RERANKER, OntologyClass.SEARCH)
            )
        await self._adapter.load()

    async def execute(self, query: str) -> RoutingResult:
        await self._ensure_loaded()
        candidate_texts = [c[2] for c in self._candidates]
        ranked = await self._adapter.rerank(query, candidate_texts, top_k=3)
        best_text, best_score = ranked[0]
        idx = candidate_texts.index(best_text)
        gateway, domain = self._candidates[idx][0], self._candidates[idx][1]
        return RoutingResult(match=True, confidence=round(float(best_score), 4),
                             gateway=gateway, domain=domain)
