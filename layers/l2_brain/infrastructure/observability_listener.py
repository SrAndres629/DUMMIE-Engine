import logging
from typing import Any

logger = logging.getLogger("brain.observability.listener")

class ObservabilityListener:
    """
    [L2_BRAIN] Listener de auditoría industrial.
    Persiste eventos del bus en el grafo (Kuzu) o logs estructurados.
    """
    def __init__(self, event_bus):
        self.bus = event_bus
        self.bus.subscribe("ToolSelection", self.on_tool_selection)

    async def on_tool_selection(self, event: Any):
        # En una arquitectura industrial, aquí iría la escritura a Kuzu
        # Por ahora, validamos la recepción estructurada
        logger.info(f"AUDIT_RECORD: {event}")
        # Placeholder para persistencia: self.kuzu.save(event)
