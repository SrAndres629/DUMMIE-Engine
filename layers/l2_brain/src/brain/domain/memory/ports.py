"""
Memory Domain Ports (L2_Brain)

Define las interfaces (Hexagonal Ports) que deben ser implementadas
por los adaptadores en la capa de infraestructura.
Asegura que el Dominio no dependa de implementaciones físicas (KùzuDB, Redb, etc).
"""

from typing import Protocol, List, Optional
from brain.domain.memory.models import MemoryNode4DTES, CrystallizedSkill
from brain.domain.governance.models import DecisionRecord, LayerCertainty

class IEventStorePort(Protocol):
    """
    Output Port para la persistencia inmutable del 4D-TES.
    Maneja el almacenamiento de nodos de memoria vinculados por hashes causales.
    """
    
    def append(self, node: MemoryNode4DTES) -> None:
        """Persiste un nuevo nodo de memoria en el almacén inmutable."""
        ...
        
    def get_by_hash(self, causal_hash: str) -> Optional[MemoryNode4DTES]:
        """Recupera un nodo específico mediante su firma criptográfica."""
        ...
        
    def get_causal_chain(self, leaf_hash: str, depth: int = 30) -> List[MemoryNode4DTES]:
        """Reconstruye la genealogía de eventos hacia atrás en el tiempo."""
        ...

    def get_last_leaf_hash(self, locus_x: str = None) -> str:
        """Recupera el hash del último nodo (head) de la cadena causal. Retorna 'GENESIS' si no hay nodos."""
        ...


class ILedgerAuditPort(Protocol):
    """
    Output Port para el Ledger de Decisiones (Spec 34).
    Garantiza la inmutabilidad de las resoluciones de diseño.
    """
    
    def record_decision(self, record: DecisionRecord) -> None:
        """Registra una decisión vinculante en el ledger persistente."""
        ...
        
    def get_decisions_for_locus(self, x: str, y: str, z: str) -> List[DecisionRecord]:
        """Recupera el historial de decisiones para un punto específico del espacio ontológico."""
        ...
        
    def get_certainty_for_locus(self, locus_x: str) -> LayerCertainty:
        """Calcula la certeza ontológica basada en el historial de decisiones y tests."""
        ...


class ISkillRepositoryPort(Protocol):
    """
    Output Port para la Memoria Procedimental Cristalizada (Spec 38).
    Almacena habilidades destiladas y validadas.
    """
    
    def save_skill(self, skill: CrystallizedSkill) -> None:
        """Persiste una habilidad cristalizada en el repositorio de Skills."""
        ...
        
    def get_skill_by_id(self, skill_id: str) -> Optional[CrystallizedSkill]:
        """Recupera una habilidad específica por su ID."""
        ...


class IShieldOutputPort(Protocol):
    """
    Output Port hacia L3 (Escudo).
    Utilizado para validar intenciones contra el sistema de seguridad.
    """
    def audit_intent(self, intent_json: str) -> dict:
        """Envía una intención al Escudo para su firma/veto."""
        ...

