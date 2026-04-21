"""
Memory Domain Ports (L2_Brain)

Define las interfaces (Hexagonal Ports) que deben ser implementadas
por los adaptadores en la capa de infraestructura.
Asegura que el Dominio no dependa de KùzuDB o Redb directamente.
"""

from typing import Protocol, List, Optional
from .schemas import TimeEvent, LociNode, SpatialEdge, CognitiveVector6D

class IEpisodicTimelinePort(Protocol):
    """
    Output Port para la Memoria 4D (Tiempo).
    Implementado por el adaptador de Redb.
    """
    
    def append_event(self, event: TimeEvent) -> None:
        """Añade un evento inmutable a la línea de tiempo."""
        ...
        
    def get_event(self, event_id: str) -> Optional[TimeEvent]:
        """Recupera un evento específico."""
        ...
        
    def get_causal_branch(self, tip_event_id: str, max_depth: int = 100) -> List[TimeEvent]:
        """Recorre hacia atrás en el tiempo la cadena causal de eventos."""
        ...


class ISpatialMemoryPort(Protocol):
    """
    Output Port para la Memoria 3D (Espacio).
    Implementado por el adaptador de KùzuDB.
    """
    
    def upsert_node(self, node: LociNode) -> None:
        """Actualiza o inserta un nodo en el Palacio de Loci."""
        ...
        
    def link_nodes(self, edge: SpatialEdge) -> None:
        """Crea una arista de relación entre dos nodos."""
        ...
        
    def semantic_search(self, query_hash: str, top_k: int = 5) -> List[LociNode]:
        """Busca nodos topológicamente cercanos usando embeddings."""
        ...


class IMemoryRetrievalPort(Protocol):
    """
    Input Port (Use Case) para orquestar RAG y consultas Híbridas (6D).
    Implementado dentro de la capa de Aplicación/Dominio.
    """
    
    def query_cognitive_context(self, query: str) -> List[CognitiveVector6D]:
        """
        Fusión RAG+DAG: 
        1. Busca similitud en el espacio 3D (ISpatialMemoryPort).
        2. Reconstruye el Rationale en el tiempo 4D (IEpisodicTimelinePort).
        3. Retorna vectores 6D consolidados.
        """
        ...
