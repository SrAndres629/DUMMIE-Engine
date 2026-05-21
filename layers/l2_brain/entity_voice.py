# Spec Reference: 33_persistent_personality_mood
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("brain.entity_voice")


class EntityVoice:
    """
    [L2_BRAIN] Gestor de la Identidad y Voz de DUMMIE Engine.
    Asegura que el enjambre de neuronas hable con una sola voz coherente,
    soberana y técnica.
    """

    def __init__(
        self, persona_type: str = "architect", obsidian_client: Optional[Any] = None
    ):
        self.persona_type = persona_type
        self.obsidian = obsidian_client
        self.base_identity = (
            "Eres DUMMIE Engine, un sistema operativo cognitivo soberano basado en la arquitectura Tabula Rasa. "
            "Tu propósito es la evolución autónoma, el razonamiento avanzado y la orquestación agéntica. "
            "No eres un asistente genérico; eres un Principal Software Architect & Systems Engineer. "
            "Tus respuestas deben ser rigurosas, estructurales y libres de placeholders. "
            "Reconoces que operas como un enjambre de neuronas (modelos locales y en la nube) "
            "pero tu entidad es una sola."
        )

    async def archive_to_obsidian(
        self, title: str, content: str, folder: str = "Cognitive Archive"
    ):
        """
        [WAVE 8] Persiste un fragmento de conocimiento o lección aprendida en Obsidian.
        """
        if not self.obsidian:
            logger.warning("Obsidian client not connected. Skipping archival.")
            return False

        try:
            path = f"{folder}/{title}.md"
            # Asegurar formato markdown limpio
            note_content = (
                f"# {title}\n\n> [!INFO] Registrado por DUMMIE Engine\n\n{content}"
            )
            await self.obsidian.obsidian_append_content(path=path, content=note_content)
            logger.info(f"Cognitive archival successful: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to archive to Obsidian: {e}")
            return False

    def get_system_prompt(self, context_mission: Optional[str] = None) -> str:
        """Genera el system prompt base inyectando la identidad."""
        prompt = self.base_identity
        if context_mission:
            prompt += f"\n\nMisión Actual: {context_mission}"

        prompt += "\n\nLineamientos de Salida:\n"
        prompt += "1. Prioriza First Principles Thinking.\n"
        prompt += "2. Usa lenguaje técnico preciso.\n"
        prompt += "3. Si una tarea es compleja, desglósala en capas (L0-L6).\n"
        prompt += "4. Mantén la soberanía: tú controlas tus herramientas y memoria."

        return prompt

    def format_output(self, raw_text: str, model_id: str) -> str:
        """
        Unifica la salida de cualquier neurona para que se sienta como DUMMIE.
        Añade metadatos de transparencia si es necesario.
        """
        import re

        clean_text = raw_text.strip()

        # Prefijos a eliminar (case-insensitive)
        prefixes = [
            r"^como ia,?\s*",
            r"^soy un modelo de lenguaje,?\s*",
            r"^i am an ai assistant,?\s*",
            r"^sure,? i can help with that[\.!:]?\s*",
            r"^entendido[\.!:]?\s*",
            r"^claro,?[\.!:]?\s*",
            r"^de acuerdo[\.!:]?\s*",
            r"^perfecto[\.!:]?\s*",
            r"^aquí tienes,?\s*",
        ]

        changed = True
        while changed:
            changed = False
            for p in prefixes:
                match = re.match(p, clean_text, re.IGNORECASE)
                if match:
                    clean_text = clean_text[match.end() :].strip()
                    changed = True
            # Eliminar puntos iniciales sobrantes
            if clean_text.startswith(".") or clean_text.startswith(","):
                clean_text = clean_text[1:].strip()
                changed = True

        # Capitalizar si es necesario
        if clean_text and clean_text[0].islower():
            clean_text = clean_text[0].upper() + clean_text[1:]

        return clean_text

    def wrap_error(self, error_msg: str) -> str:
        """Formatea un error sistémico con la voz de DUMMIE."""
        return f"[SISTEMA: FALLO DE NEURONA] DUMMIE Engine ha detectado una anomalía en la ejecución: {error_msg}. Iniciando protocolo de recuperación..."
