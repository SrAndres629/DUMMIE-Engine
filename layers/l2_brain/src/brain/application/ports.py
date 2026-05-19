from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

# Spec: 166_l2_brain_organ_migration_contract
# Compatibility: this legacy module also acts as a namespace package so
# brain.application.ports.kernel_ports and capsule_ports keep resolving.
__path__ = [str(Path(__file__).with_suffix(""))]

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
