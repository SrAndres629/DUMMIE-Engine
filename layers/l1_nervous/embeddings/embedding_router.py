from .embedding_service import EmbeddingService
from .embedding_cache import EmbeddingCache

DOMAIN_PROTOTYPES = {
    "media_generation": "generar imagen video audio contenido multimedia",
    "vcs": "git commit push pull branch repository code version",
    "workspace_io": "leer archivo escribir archivo filesystem",
    "infrastructure": "docker container deploy cloud infrastructure",
    "shell_execution": "ejecutar comando shell terminal bash",
    "browser_automation": "navegar web browser test automatico",
    "structured_knowledge": "base de datos sql query memoria conocimiento",
    "reasoning_support": "razonar pensar planificar analizar",
}


class EmbeddingRouter:
    def __init__(self):
        self.service = EmbeddingService()
        self.cache = EmbeddingCache(default_ttl=300.0)
        self.domain_vectors = {
            name: self.service.embed_one(text)
            for name, text in DOMAIN_PROTOTYPES.items()
        }

    def route(self, query: str, threshold: float = 0.35) -> list[tuple[str, float]]:
        cached = self.cache.get(f"route:{query}")
        if cached:
            return cached
        qvec = self.service.embed_one(query)
        scores = [
            (name, self.service.similarity(qvec, dvec))
            for name, dvec in self.domain_vectors.items()
        ]
        scores.sort(key=lambda x: -x[1])
        result = [(name, score) for name, score in scores if score >= threshold]
        self.cache.set(f"route:{query}", result, ttl=60.0)
        return result

    def best_domain(self, query: str, threshold: float = 0.35):
        results = self.route(query, threshold)
        return results[0] if results else None
