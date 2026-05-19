import os
import httpx
import asyncio
import logging
from typing import List, Dict, Any, Optional
from model_router import ModelConfig, ModelTier, ModelRegistry

logger = logging.getLogger("brain.discovery")

class ModelDiscoveryService:
    """
    [L2_BRAIN] Servicio de descubrimiento dinámico de neuronas.
    Escanea proveedores locales y remotos para construir el ModelRegistry.
    """
    def __init__(self, ollama_url: str = "http://127.0.0.1:11434"):
        self.ollama_url = ollama_url
        self.groq_key = os.getenv("DUMMIE_GROQ_API_KEY", "")
        self.openrouter_key = os.getenv("DUMMIE_OPENROUTER_API_KEY", "")

    async def discover_all(self) -> ModelRegistry:
        registry = ModelRegistry()
        
        # 1. Discover Ollama (Local)
        local_models = await self._discover_ollama()
        for tier, configs in local_models.items():
            if tier not in registry.models: registry.models[tier] = []
            registry.models[tier].extend(configs)
            
        # 2. Discover Groq (Cloud Free/Fast)
        groq_models = await self._discover_groq()
        for tier, configs in groq_models.items():
            if tier not in registry.models: registry.models[tier] = []
            registry.models[tier].extend(configs)

        # 3. Discover OpenRouter (Cloud Multi)
        if self.openrouter_key:
            or_models = await self._discover_openrouter()
            for tier, configs in or_models.items():
                if tier not in registry.models: registry.models[tier] = []
                registry.models[tier].extend(configs)

        # 4. Defaults if nothing found
        self._ensure_defaults(registry)
        
        logger.info(f"Discovery: Registered {sum(len(v) for v in registry.models.values())} models across {len(registry.models)} tiers.")
        return registry

    async def _discover_ollama(self) -> Dict[ModelTier, List[ModelConfig]]:
        results = {ModelTier.LOCAL_FAST: [], ModelTier.LOCAL_DEEP: []}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.ollama_url}/api/tags", timeout=2.0)
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    for m in models:
                        name = m["name"]
                        # Heurística simple: nombres con 'e' o '26b' etc
                        tier = ModelTier.LOCAL_DEEP if "26b" in name or "70b" in name else ModelTier.LOCAL_FAST
                        results[tier].append(ModelConfig(
                            model_id=name,
                            tier=tier,
                            provider="ollama",
                            base_url=self.ollama_url,
                            timeout_s=15.0 if tier == ModelTier.LOCAL_DEEP else 5.0
                        ))
        except Exception as e:
            logger.warning(f"Ollama discovery failed: {e}")
        return results

    async def _discover_groq(self) -> Dict[ModelTier, List[ModelConfig]]:
        results = {ModelTier.CLOUD_STD: []}
        if not self.groq_key: return results
        
        # Groq models are usually Llama3-8b, Llama3-70b, Mixtral-8x7b
        # For simplicity, we hardcode some known fast ones for CLOUD_STD
        # In the future, we could query their API if available
        known_models = ["llama3-8b-8192", "mixtral-8x7b-32768", "llama3-70b-8192"]
        for m_id in known_models:
            results[ModelTier.CLOUD_STD].append(ModelConfig(
                model_id=m_id,
                tier=ModelTier.CLOUD_STD,
                provider="openai_compat",
                base_url="https://api.groq.com/openai/v1",
                api_key_env="DUMMIE_GROQ_API_KEY",
                timeout_s=10.0
            ))
        return results

    async def _discover_openrouter(self) -> Dict[ModelTier, List[ModelConfig]]:
        results = {ModelTier.CLOUD_PREM: []}
        # Placeholder for OpenRouter discovery
        # results[ModelTier.CLOUD_PREM].append(...)
        return results

    def _ensure_defaults(self, registry: ModelRegistry):
        # Fallback manual if discovery empty
        if not registry.models.get(ModelTier.LOCAL_FAST):
             registry.models[ModelTier.LOCAL_FAST] = [ModelConfig(model_id="gemma4:e4b", tier=ModelTier.LOCAL_FAST, provider="ollama", base_url=self.ollama_url)]
