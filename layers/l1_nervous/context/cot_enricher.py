class CoTEnricher:
    def __init__(self, context_engine=None):
        from .context_engine import ContextEngine

        self._engine = context_engine or ContextEngine()

    def register_dimension(self, dim):
        self._engine.register(dim)

    async def build_cot_prompt(self, query: str, active_dims: list[str] = None) -> str:
        profile = await self._engine.build_profile(active_dims)
        context_block = profile.to_prompt()
        return f"""[SISTEMA]: Eres un router con Chain of Thought profundo.
Tienes acceso a 6 dimensiones de contexto para tomar la mejor decisión.

{context_block}

[CONSULTA]: {query}

[INSTRUCCIONES CoT]:
1. Analiza la consulta semánticamente (D3)
2. Relaciona con el contexto temporal (D1) y espacial (D2)
3. Consulta la ontología de relaciones (D4)
4. Revisa memoria episódica de decisiones anteriores (D5)
5. Evalúa herramientas disponibles (D6)
6. Genera razonamiento paso a paso
7. Decide dominio, gateway y acción

[RESPUESTA JSON]:
{{
  "reasoning": "razonamiento paso a paso...",
  "domain": "dominio_elegido",
  "gateway": "gateway_elegido",
  "tool": "herramienta_sugerida",
  "confidence": 0.0-1.0,
  "ontology_class": "semantic|reasoning|code|search|memory",
  "needs_clarification": false,
  "clarifying_question": "pregunta si es necesario"
}}"""
