import logging
from typing import Dict, Any, Tuple
from auditor_port import BaseAuditor

logger = logging.getLogger("shield-structural")

class TopologicalAuditor(BaseAuditor):
    """
    [L3_SHIELD] Adaptador de Seguridad Estructural.
    Implementa el BaseAuditor de L2 para proporcionar validación topológica.
    """
    def __init__(self, kuzu_adapter: Any = None):
        self.kuzu = kuzu_adapter

    async def audit(self, dag_xml: str, goal: str = "") -> Tuple[bool, str]:
        """
        Analiza el DAG en busca de anomalías estructurales reales.
        """
        logger.info(f"S-SHIELD: Auditing DAG topology for goal: {goal}")
        
        # [L3 HARDENING] Validación de Ciclos Real mediante parsing
        try:
            import xml.etree.ElementTree as ET
            from collections import defaultdict

            # Si es un string simple que no parece XML, fallback al auditor anterior (pero logeando advertencia)
            if not dag_xml.strip().startswith("<"):
                if "cycle" in dag_xml.lower():
                    return False, "DETECTION_ANOMALY: Circular dependency detected in raw text."
                return True, "TOPOLOGY_VALIDATED_LEGACY"

            root = ET.fromstring(dag_xml)
            adj = defaultdict(list)
            # Asumimos formato simple: <edge source="A" target="B"/>
            for edge in root.findall(".//edge"):
                u = edge.get("source")
                v = edge.get("target")
                if u and v:
                    adj[u].append(v)

            # Algoritmo de detección de ciclos (DFS)
            visited = set()
            rec_stack = set()

            def has_cycle(v):
                visited.add(v)
                rec_stack.add(v)
                for neighbour in adj[v]:
                    if neighbour not in visited:
                        if has_cycle(neighbour):
                            return True
                    elif neighbour in rec_stack:
                        return True
                rec_stack.remove(v)
                return False

            for node in list(adj.keys()):
                if node not in visited:
                    if has_cycle(node):
                        return False, f"DETECTION_ANOMALY: Cycle detected starting from node {node}"

            return True, "TOPOLOGY_VALIDATED_DAG"

        except Exception as e:
            logger.error(f"Auditor Failure: {e}")
            return False, f"AUDIT_SYSTEM_ERROR: {str(e)}"

    def calculate_entropy(self, nodes: int, edges: int) -> float:
        if nodes == 0: return 0.0
        return edges / nodes
