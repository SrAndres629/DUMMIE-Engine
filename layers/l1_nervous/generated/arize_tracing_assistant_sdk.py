from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para arize-tracing-assistant
# NO EDITAR DIRECTAMENTE.

class ArizeTracingAssistantClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def get_arize_tracing_docs(self, **kwargs) -> Any:
        """ Get docs and examples to instrument an app and send traces/spans to Arize. If the framework is not in the list use manual instrumentation with open telemetry.  Parameters ---------- framework : str     LLM provider or framework. One of:     ["agno", "amazon-bedrock", "anthropic", "autogen", "beeai", "crewai", "dspy", "google-gen-ai", "groq", "guardrails-ai", "haystack",     "hugging-face-smolagents", "instructor", "langchain", "langflow", "langgraph", "litellm", "llamaindex", "mistralai", "openai", "openai-agents", "prompt-flow",     "pydantic-ai", "strands-agents", "together", "vercel", "vertexai"] language : str     Programming language: "python" or "typescript"  Returns ------- str     Example code snippets for auto/manual instrumentation for Arize. """
        return await self.proxy.call_tool('arize-tracing-assistant', 'get_arize_tracing_docs', kwargs)

    async def get_arize_advanced_tracing_docs(self, **kwargs) -> Any:
        """ Get advanced docs and examples to manually instrument an app and send traces/spans to Arize.   Parameters ----------: language: str     "python" or "typescript" or "javascript"  Returns: str     Docs and code snippets for advanced instrumentation. """
        return await self.proxy.call_tool('arize-tracing-assistant', 'get_arize_advanced_tracing_docs', kwargs)

    async def arize_support(self, **kwargs) -> Any:
        """Send *message* to the `search` tool and return the assistant reply.  Parameters ---------- message : str     The user message to send to the assistant.  Returns ------- str     The assistant's textual response. """
        return await self.proxy.call_tool('arize-tracing-assistant', 'arize_support', kwargs)
