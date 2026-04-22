from abc import ABC, abstractmethod

class IBrainOrchestrator(ABC):
    """
    Input Port para la orquestación cognitiva en L2.
    Define cómo los agentes interactúan con el "Cerebro".
    """
    @abstractmethod
    async def handle_task(self, payload: str) -> str:
        """Procesa una tarea y retorna el estado de validación."""
        pass
