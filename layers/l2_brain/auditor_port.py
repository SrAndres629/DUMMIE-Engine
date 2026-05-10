from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from gateway_contract import GatewayRequest

class BaseAuditor(ABC):
    """
    [PORT] Interfaz abstracta para la validación de seguridad y topología.
    Permite que L2 (Brain) delegue el juicio a L3 (Shield).
    """
    @abstractmethod
    async def audit(self, dag_xml: str, goal: str = "") -> Tuple[bool, str]:
        pass

class BaseExecutor(ABC):
    """
    [PORT] Interfaz abstracta para la ejecución física.
    Desacopla la orquestación del transporte (MCP/Local).
    """
    @abstractmethod
    async def execute(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        pass
