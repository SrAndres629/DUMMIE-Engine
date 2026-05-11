import json
import urllib.request
from typing import List
from brain.domain.memory.ports import IEmbeddingPort

class OllamaEmbeddingAdapter(IEmbeddingPort):
    """
    Adaptador para generar embeddings usando Ollama (Gemma 2).
    Implementa la Spec de Local Semantic Search para ahorro de tokens.
    """
    def __init__(self, host: str = "http://localhost:11434", model: str = "gemma2:2b"):
        self.host = host
        self.model = model
        self.endpoint = f"{self.host}/api/embeddings"

    def generate_embedding(self, text: str) -> List[float]:
        """Llamada sincrónica a la API de Ollama."""
        data = {
            "model": self.model,
            "prompt": text
        }
        
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("embedding", [])
        except Exception as e:
            print(f"[OllamaEmbeddingAdapter] Error generando embedding: {e}")
            return []

    async def generate_embedding_async(self, text: str) -> List[float]:
        """
        Versión asíncrona (usando run_in_executor para no bloquear el loop).
        Ideal para el CognitiveOrchestrator.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_embedding, text)
