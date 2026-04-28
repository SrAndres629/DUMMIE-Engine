from abc import ABC, abstractmethod
from typing import List, Dict, Any

class CodeAnalysisPort(ABC):
    """Puerto para análisis estático y comprensión de código."""
    
    @abstractmethod
    async def analyze_symbols(self, path: str) -> List[Dict[str, Any]]:
        pass

class ObservabilityPort(ABC):
    """Puerto para inyección de telemetría y trazas."""
    
    @abstractmethod
    async def record_trace(self, session_id: str, action: str, status: str) -> None:
        pass
