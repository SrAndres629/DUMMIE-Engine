import logging

logger = logging.getLogger("dummie-mcp.context.socratic")


class SocraticBridge:
    def __init__(self, llm_adapter=None):
        self._adapter = llm_adapter

    async def clarify(self, query: str, context: str = "") -> list[str]:
        prompt = f"""Eres un asistente Socrático. Dada una consulta ambigua, genera preguntas clarificadoras.

Contexto: {context or "ninguno"}
Consulta: {query}

Genera 1-3 preguntas que ayuden a desambiguar la intención del usuario.
Devuelve JSON: {{"questions": ["pregunta 1?", "pregunta 2?"]}}"""

        if self._adapter:
            try:
                result = await self._adapter.generate_json(prompt, "")
                return result.get("questions", [])
            except Exception:
                pass
        return self._default_questions(query)

    def _default_questions(self, query: str) -> list[str]:
        q = query.lower()
        questions = []
        if any(w in q for w in ["imagen", "image", "video", "audio"]):
            questions.append(
                "¿Qué tipo de contenido multimedia quieres generar (imagen, video o audio)?"
            )
        if any(w in q for w in ["git", "commit", "repo"]):
            questions.append("¿Qué acción de git necesitas realizar?")
        if not questions:
            questions.append(
                "¿Podrías proporcionar más detalles sobre lo que necesitas?"
            )
        return questions

    async def analyze(self, query: str, context: str = "") -> dict:
        prompt = f"""Analiza esta consulta socráticamente:
Consulta: {query}
Contexto: {context or "ninguno"}

Devuelve JSON:
{{
  "understood": true/false,
  "intent": "intención del usuario",
  "missing_info": ["qué falta para entender"],
  "clarifying_questions": ["preguntas"],
  "confidence": 0.0-1.0
}}"""
        if self._adapter:
            try:
                return await self._adapter.generate_json(prompt, "")
            except Exception:
                pass
        return {"understood": False, "intent": "unknown", "confidence": 0.0}
