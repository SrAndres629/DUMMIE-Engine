import time
import math
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class EpistemicNode(BaseModel):
    causal_hash: str
    parent_hashes: List[str]
    payload: str
    payload_hash: str
    lamport_t: int
    authority_a: str
    intent_i: str
    similarity_score: float = 0.0

class RetrievalService:
    """
    Servicio de Dominio encargado del filtrado y ordenamiento epistémico de recuerdos.
    """
    
    @staticmethod
    def calculate_epistemic_score(
        node: EpistemicNode,
        query_sim: float,
        alpha: float = 0.4,
        beta: float = 0.2,
        gamma: float = 0.2,
        eta: float = 0.2,
        zeta: float = 0.3,
        current_lamport_t: Optional[int] = None
    ) -> float:
        """
        Implementa la ecuación de ranking epistémico:
        s(v) = alpha*sim(v,q) + beta*authority(v) + gamma*freshness(v) + eta*proof(v) - zeta*conflict(v)
        """
        import json
        import math
        import time
        
        # 1. Extracción de campos epistémicos
        pi_confidence = 1.0
        rho_risk = 0.0
        evidence_count = 0
        
        try:
            payload_data = json.loads(node.payload)
            if isinstance(payload_data, dict):
                # Si viene encapsulado en "content"
                cdata = payload_data.get("content")
                if isinstance(cdata, dict):
                    pi_confidence = float(cdata.get("pi_confidence", 1.0))
                    rho_risk = float(cdata.get("rho_risk", 0.0))
                    evidence_count = len(cdata.get("evidence_hashes", []))
                else:
                    pi_confidence = float(payload_data.get("pi_confidence", 1.0))
                    rho_risk = float(payload_data.get("rho_risk", 0.0))
                    evidence_count = len(payload_data.get("evidence_hashes", []))
        except Exception:
            # Payload legacy plano
            pass

        # 2. Authority Score
        authority_weights = {
            "HUMAN": 1.0,
            "ARCHITECT": 0.9,
            "OVERSEER": 0.7,
            "ENGINEER": 0.6,
            "AGENT": 0.4,
            "AUTHORITY_UNSPECIFIED": 0.2
        }
        auth_score = authority_weights.get(str(node.authority_a).upper(), 0.2)

        # 3. Freshness Score (Decaimiento temporal)
        if int(node.lamport_t) > 1000000000:  # Parece Unix Time
            time_diff = abs(int(time.time()) - int(node.lamport_t))
            freshness = math.exp(-time_diff / 86400.0)
        else:
            # Parece Lamport lógico
            if current_lamport_t is not None and current_lamport_t > 0:
                tick_diff = max(0, current_lamport_t - int(node.lamport_t))
                freshness = math.exp(-tick_diff / 50.0)  # Ventana de 50 ticks
            else:
                freshness = 1.0

        # 4. Proof Score
        proof_score = min(1.0, evidence_count / 5.0)

        # 5. Conflict Score
        conflict_score = (1.0 - pi_confidence) + rho_risk

        # Cálculo final
        total_score = (
            alpha * query_sim +
            beta * auth_score +
            gamma * freshness +
            eta * proof_score -
            zeta * conflict_score
        )
        return total_score

    @classmethod
    def rank_nodes(
        cls, 
        nodes: List[Any], 
        query_similarities: List[float],
        alpha: float = 0.4
    ) -> List[Any]:
        """
        Ordena los nodos devolviendo los subgrafos con mayor valor de información epistémica.
        """
        # Obtener el máximo tick de Lamport
        max_lamport = 0
        for n in nodes:
            lt = int(getattr(n, "lamport_t", 0))
            if lt > max_lamport:
                max_lamport = lt

        scored_nodes = []
        for i, node in enumerate(nodes):
            sim = query_similarities[i] if i < len(query_similarities) else 0.0
            
            # Envoltorio para tipado
            enode = EpistemicNode(
                causal_hash=getattr(node, "causal_hash", ""),
                parent_hashes=getattr(node, "parent_hashes", ["GENESIS"]),
                payload=getattr(node, "payload", ""),
                payload_hash=getattr(node, "payload_hash", ""),
                lamport_t=getattr(node, "lamport_t", int(time.time())),
                authority_a=str(getattr(node, "authority_a", "AGENT")),
                intent_i=str(getattr(node, "intent_i", "FABRICATION")),
                similarity_score=sim
            )
            
            score = cls.calculate_epistemic_score(
                enode, sim, alpha=alpha, current_lamport_t=max_lamport
            )
            scored_nodes.append((score, node))
            
        # Ordenar descendentemente por score epistémico
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_nodes]

    @classmethod
    def extract_minimal_proof_subgraph(
        cls,
        start_node: Any,
        get_node_by_hash: Any,  # Callable[[str], Any]
        query_sim: float,
        tau_threshold: float = 0.8,
        max_depth: int = 5
    ) -> List[Any]:
        """
        Extrae el certificado causal mínimo (S*) que justifica una acción.
        Resuelve: argmin |S| sujeto a I(Y;S|q) >= tau.
        Modelamos I(Y;S|q) = 1.0 - prod(1.0 - epistemic_score(v)).
        """
        subgraph = []
        visited = set()
        queue = [(start_node, 0)] # (nodo, profundidad)
        
        # Probabilidad residual de incertidumbre
        residual_uncertainty = 1.0
        
        while queue:
            current_node, depth = queue.pop(0)
            
            c_hash = getattr(current_node, "causal_hash", "")
            if not c_hash or c_hash in visited:
                continue
                
            visited.add(c_hash)
            subgraph.append(current_node)
            
            # Envoltorio para cálculo
            enode = EpistemicNode(
                causal_hash=c_hash,
                parent_hashes=getattr(current_node, "parent_hashes", ["GENESIS"]),
                payload=getattr(current_node, "payload", ""),
                payload_hash=getattr(current_node, "payload_hash", ""),
                lamport_t=getattr(current_node, "lamport_t", int(time.time())),
                authority_a=str(getattr(current_node, "authority_a", "AGENT")),
                intent_i=str(getattr(current_node, "intent_i", "FABRICATION")),
                similarity_score=query_sim if depth == 0 else (query_sim * math.exp(-depth))
            )
            
            # Epistemic Score como confianza [0, 1]
            score = min(1.0, max(0.0, cls.calculate_epistemic_score(enode, enode.similarity_score)))
            
            # Disminuir la incertidumbre
            residual_uncertainty *= (1.0 - score)
            
            # Información Mutua Condicional aproximada
            info_gain = 1.0 - residual_uncertainty
            
            if info_gain >= tau_threshold:
                break
                
            if depth < max_depth:
                parent_hashes = enode.parent_hashes
                for phash in parent_hashes:
                    if phash != "GENESIS" and phash not in visited:
                        try:
                            parent_node = get_node_by_hash(phash)
                            if parent_node:
                                queue.append((parent_node, depth + 1))
                        except Exception:
                            pass
                            
        return subgraph
