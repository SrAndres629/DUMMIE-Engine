from .pipeline import RoutingResult, RoutingStrategy

DOMAIN_PROTOTYPES = {
    "media_generation": ("media", "generar imagen video audio contenido multimedia"),
    "vcs": ("code", "git commit push pull branch repository"),
    "workspace_io": ("code", "leer archivo escribir archivo filesystem"),
    "infrastructure": ("infra", "docker container deploy cloud infrastructure"),
    "shell": ("shell", "ejecutar comando shell terminal bash"),
    "knowledge": ("knowledge", "base de datos sql query memoria conocimiento"),
}

class EmbeddingMatchStrategy:
    name = "embedding_match"

    def __init__(self, registry=None):
        self.registry = registry
        self._adapter = None
        self._domain_vectors = None

    async def _ensure_loaded(self):
        if self._adapter is not None:
            return
        if self.registry:
            self._adapter = self.registry.get_or_create("BAAI/bge-small-en-v1.5")
        else:
            from ...models.adapters.fastembed_adapter import FastEmbedAdapter
            from ...models.adapters.base import ModelSpec, ModelType, OntologyClass
            spec = ModelSpec("BAAI/bge-small-en-v1.5", ModelType.EMBEDDING, OntologyClass.SEMANTIC)
            self._adapter = FastEmbedAdapter.get_instance(spec)
        await self._adapter.load()
        self._domain_vectors = {
            name: self._adapter.embed_one(text)
            for name, (_gw, text) in DOMAIN_PROTOTYPES.items()
        }

    async def execute(self, query: str) -> RoutingResult:
        await self._ensure_loaded()
        qvec = self._adapter.embed_one(query)
        scores = [(name, gw, self._adapter.similarity(qvec, dvec))
                  for name, (gw, _text), dvec in
                  [(n, *[DOMAIN_PROTOTYPES[n][0], v])
                   for n, v in self._domain_vectors.items()]]
        scores.sort(key=lambda x: -x[2])
        if scores and scores[0][2] > 0.35:
            domain, gateway, confidence = scores[0]
            return RoutingResult(match=True, gateway=gateway, domain=domain, confidence=round(confidence, 4))
        return RoutingResult(match=False, confidence=0.0)
