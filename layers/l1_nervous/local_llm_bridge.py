import json
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger("dummie-mcp.llm-bridge")

OLLAMA_MODEL = "gemma3:1b"
OLLAMA_HOST = "http://localhost:11434"
LLM_TIMEOUT = 30

LLM_REASONING_SYSTEM_PROMPT = """Eres un arquitecto de sistemas evaluando qué herramienta MCP o skill es la mejor para una tarea. Tu trabajo es analizar el contexto y la consulta, y determinar si existe una herramienta adecuada.

REGLAS:
1. Si existe UNA herramienta exacta → devuélvela con confidence=1.0
2. Si varias herramientas pueden servir → elige la MEJOR y explica por qué
3. Si NINGUNA herramienta sirve exactamente → sugiere la más cercana y describe cómo adaptarla
4. Si no hay NADA similar → propón preguntas metacognitivas para ayudar al modelo a refinar su búsqueda

Siempre devuelve SOLO JSON válido con esta estructura:
{
  "suggested_tool": "tool_id o null",
  "confidence": 0.0-1.0,
  "reasoning": "explicacion detallada de por que esta herramienta fue seleccionada o por que no hay match",
  "adaptation": "como adaptar la tool existente si no hay match exacto, o null",
  "metacognitive_questions": ["pregunta util 1", "pregunta util 2"],
  "needs_more_context": ["campo_faltante_1"]
}"""


@dataclass
class LLMDecision:
    suggested_tool: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""
    adaptation: Optional[str] = None
    metacognitive_questions: list = field(default_factory=list)
    needs_more_context: list = field(default_factory=list)
    llm_available: bool = False
    latency_ms: float = 0.0


class LocalLLMBridge:
    def __init__(self):
        self._available = self._check_ollama()
        self._llm = None
        if self._available:
            try:
                import ollama

                self._llm = ollama
                logger.info("LocalLLMBridge: ollama disponible (%s)", OLLAMA_MODEL)
            except ImportError:
                logger.warning("LocalLLMBridge: ollama Python SDK no instalado")
                self._available = False
        else:
            logger.info("LocalLLMBridge: ollama no disponible, modo fallback")

    def _check_ollama(self) -> bool:
        try:
            import urllib.request

            req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read())
                models = data.get("models", [])
                if not models:
                    logger.warning("ollama OK pero sin modelos instalados")
                    return False
                logger.info("ollama OK: %d modelos disponibles", len(models))
                return True
        except Exception as e:
            logger.debug("ollama no disponible: %s", e)
            return False

    def reason(
        self,
        query: str,
        context: dict = None,
        tools_summary: str = "",
        skills_summary: str = "",
    ) -> LLMDecision:
        start = time.time()
        if not self._available or not self._llm:
            return LLMDecision(
                llm_available=False,
                latency_ms=(time.time() - start) * 1000,
                reasoning="LLM local no disponible",
            )

        prompt = self._build_prompt(query, context, tools_summary, skills_summary)

        try:
            resp = self._llm.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": LLM_REASONING_SYSTEM_PROMPT,
                    },
                    {"role": "user", "content": prompt},
                ],
                options={
                    "num_ctx": 2048,
                    "num_predict": 512,
                    "temperature": 0.1,
                },
            )

            content = resp.get("message", {}).get("content", "")
            decision = self._parse_response(content)
            decision.llm_available = True
            decision.latency_ms = (time.time() - start) * 1000
            logger.debug(
                "LLM decision: tool=%s confidence=%.2f latency=%.0fms",
                decision.suggested_tool,
                decision.confidence,
                decision.latency_ms,
            )
            return decision

        except Exception as e:
            logger.error("LLM inference error: %s", e)
            return LLMDecision(
                llm_available=True,
                latency_ms=(time.time() - start) * 1000,
                reasoning=f"Error en LLM: {e}",
            )

    def _build_prompt(
        self,
        query: str,
        context: dict = None,
        tools_summary: str = "",
        skills_summary: str = "",
    ) -> str:
        ctx = context or {}
        return f"""CONSULTA DEL MODELO: {query}

CONTEXTO DE SESIÓN:
- Consultas recientes: {json.dumps(ctx.get("recent_queries", []))}
- Servidores MCP activos: {json.dumps(ctx.get("active_mcps", []))}
- Proyecto activo: {ctx.get("active_project", "N/A")}

HERRAMIENTAS DISPONIBLES:
{tools_summary[:1500] if tools_summary else "N/A"}

SKILLS DISPONIBLES:
{skills_summary[:1000] if skills_summary else "N/A"}

Analiza si alguna herramienta cubre EXACTAMENTE esta necesidad. Si no, explica por qué y qué adaptación sería necesaria. Si falta contexto, genera preguntas metacognitivas."""

    def _parse_response(self, content: str) -> LLMDecision:
        try:
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            content = content.strip()
            data = json.loads(content)
            return LLMDecision(
                suggested_tool=data.get("suggested_tool"),
                confidence=data.get("confidence", 0.0),
                reasoning=data.get("reasoning", ""),
                adaptation=data.get("adaptation"),
                metacognitive_questions=data.get("metacognitive_questions", []),
                needs_more_context=data.get("needs_more_context", []),
            )
        except json.JSONDecodeError as e:
            logger.warning("LLM response parse error: %s", e)
            return LLMDecision(
                reasoning=f"No se pudo parsear respuesta del LLM: {content[:200]}"
            )
