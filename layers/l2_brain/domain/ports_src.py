from abc import ABC, abstractmethod
from typing import Dict, Any

class BrainInputPort(ABC):
    """
    Puerto de entrada para la orquestación cognitiva en L2.
    """
    @abstractmethod
    async def handle_task(self, payload: str) -> str:
        pass

class ShieldOutputPort(ABC):
    """
    Puerto de salida hacia L3 (Escudo).
    """
    @abstractmethod
    def audit_intent(self, intent_json: str) -> Dict[str, Any]:
        pass
