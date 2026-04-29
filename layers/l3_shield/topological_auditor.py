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
        Solo acepta XML válido. No hace inferencias textuales.
        """
        logger.info(f"S-SHIELD: Auditing DAG topology for goal: {goal}")

        if not dag_xml or not dag_xml.strip():
            return False, "AUDIT_ERROR: Empty DAG input."

        # [L3 HARDENING] Rechazar input no-XML de forma explícita
        stripped = dag_xml.strip()
        if not stripped.startswith("<"):
            logger.warning(
                "S-SHIELD: Received non-XML input. "
                "Text-based fallback has been removed for safety."
            )
            return False, "AUDIT_ERROR: Invalid DAG format. Expected XML."

        try:
            import xml.etree.ElementTree as ET
            from collections import defaultdict

            root = ET.fromstring(dag_xml)
            adj: Dict[str, list] = defaultdict(list)
            all_nodes: set = set()

            # Asumimos formato simple: <edge source="A" target="B"/>
            for edge in root.findall(".//edge"):
                u = edge.get("source")
                v = edge.get("target")
                if u and v:
                    adj[u].append(v)
                    all_nodes.add(u)
                    all_nodes.add(v)

            edge_count = sum(len(targets) for targets in adj.values())
            logger.info(
                f"S-SHIELD: Parsed DAG with {len(all_nodes)} nodes, "
                f"{edge_count} edges."
            )

            # Algoritmo de detección de ciclos (DFS con recursion stack)
            visited: set = set()
            rec_stack: set = set()

            def has_cycle(v: str) -> bool:
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

        except ET.ParseError as e:
            logger.error(f"S-SHIELD: XML parse error: {e}")
            return False, f"AUDIT_ERROR: Invalid XML: {str(e)}"
        except Exception as e:
            logger.error(f"Auditor Failure: {e}")
            return False, f"AUDIT_SYSTEM_ERROR: {str(e)}"

    def calculate_entropy(self, nodes: int, edges: int) -> float:
        if nodes == 0: return 0.0
        return edges / nodes
