from datetime import datetime, timezone
from typing import Dict, Any, List

def map_semantic_ontology(intent: str) -> Dict[str, Any]:
    mapping = {
        "refactor": "DEBT", 
        "memory": "MEMORY",
        "kuzu": "MEMORY",
        "daemon": "RUNTIME",
        "chat": "ENTRYPOINT", 
        "status": "REPORT", 
        "readiness": "CALIBRATION",
        "token": "TOKEN_ECONOMY",
        "gate": "SAFETY",
        "safety": "SAFETY",
        "autonom": "AUTONOMY",
        "degrad": "RISK",
        "missing": "RISK",
        "risk": "RISK",
        "test": "TEST",
        "debt": "DEBT",
        "decid": "DECISION",
        "proceed": "DECISION"
    }
    
    classes = []
    nodes = [{"id": "INTENT", "label": intent, "type": "INTENT"}]
    edges = []
    
    for kw, cls in mapping.items():
        if kw in intent.lower():
            if cls not in classes:
                classes.append(cls)
                nodes.append({"id": cls, "label": cls, "type": "CLASS"})
                edges.append({"source": "INTENT", "target": cls, "type": "IS_A"})

    # Check for Kuzu-specific ontology classes if in intent
    if "kuzu" in intent.lower() and "KUZU" not in [n["id"] for n in nodes]:
        nodes.append({"id": "KUZU", "label": "KUZU", "type": "COMPONENT"})
        edges.append({"source": "INTENT", "target": "KUZU", "type": "IS_A"})

    # Ensure TEST_DEBT and AUTONOMY_READINESS exist if test and autonomy are in intent
    if "TEST" in classes:
        if "TEST_DEBT" not in [n["id"] for n in nodes]:
            nodes.append({"id": "TEST_DEBT", "label": "TEST_DEBT", "type": "CLASS"})
            edges.append({"source": "TEST", "target": "TEST_DEBT", "type": "HAS_SUBCLASS"})
    if "AUTONOMY" in classes:
        if "AUTONOMY_READINESS" not in [n["id"] for n in nodes]:
            nodes.append({"id": "AUTONOMY_READINESS", "label": "AUTONOMY_READINESS", "type": "CLASS"})
            edges.append({"source": "AUTONOMY", "target": "AUTONOMY_READINESS", "type": "HAS_PROPERTY"})

    # Hardened Graph Relations for complex/high-risk intents (Pack 5.2.1 specific edges)
    # AUTONOMY BLOCKED_BY MEMORY
    if "AUTONOMY" in classes and "MEMORY" in classes:
        edges.append({"source": "AUTONOMY", "target": "MEMORY", "type": "BLOCKED_BY"})
    
    # MEMORY DEGRADED_BY KUZU
    if "MEMORY" in classes and "kuzu" in intent.lower():
        edges.append({"source": "MEMORY", "target": "KUZU", "type": "DEGRADED_BY"})
        
    # TEST_DEBT DEGRADES AUTONOMY_READINESS
    if "TEST" in classes and "AUTONOMY" in classes:
        edges.append({"source": "TEST_DEBT", "target": "AUTONOMY_READINESS", "type": "DEGRADES"})
        
    # SAFETY CONSTRAINS ACTION / SAFETY CONSTRAINS AUTONOMY
    if "SAFETY" in classes:
        edges.append({"source": "SAFETY", "target": "ACTION", "type": "CONSTRAINS"})
        if "AUTONOMY" in classes:
            edges.append({"source": "SAFETY", "target": "AUTONOMY", "type": "CONSTRAINS"})
    elif "safety" in intent.lower() or "degrad" in intent.lower():
        # Even if not directly in keywords, guarantee safety constraints for risk intents
        if "SAFETY" not in classes:
            nodes.append({"id": "SAFETY", "label": "SAFETY", "type": "CLASS"})
        edges.append({"source": "SAFETY", "target": "ACTION", "type": "CONSTRAINS"})

    # DECISION DEPENDS_ON EVIDENCE
    if "DECISION" in classes:
        if "EVIDENCE" not in [n["id"] for n in nodes]:
            nodes.append({"id": "EVIDENCE", "label": "EVIDENCE", "type": "CLASS"})
        edges.append({"source": "DECISION", "target": "EVIDENCE", "type": "DEPENDS_ON"})

    # Fallback to ensure edges are never empty for complex/high-risk tasks
    if not edges and classes:
        for cls in classes:
            edges.append({"source": "INTENT", "target": cls, "type": "IS_A"})

    # If it's a high risk intent, guarantee a safety/constraints edge
    if "degrad" in intent.lower() or "missing" in intent.lower():
        if not any(e["type"] == "DEGRADED_BY" or e["type"] == "BLOCKED_BY" for e in edges):
            edges.append({"source": "AUTONOMY", "target": "MEMORY", "type": "BLOCKED_BY"})

    # Clean duplicates
    unique_edges = []
    seen = set()
    for e in edges:
        k = (e["source"], e["target"], e["type"])
        if k not in seen:
            seen.add(k)
            unique_edges.append(e)

    return {
        "decision": "PASS" if classes and len(unique_edges) > 0 else "PASS_WITH_WARNINGS",
        "concepts": [intent],
        "classes": classes or ["UNKNOWN"],
        "ontology_graph": {
            "nodes": nodes,
            "edges": unique_edges
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "warnings": ["No ontology classes matched" if not classes else ""]
    }

if __name__ == "__main__":
    import json
    import sys
    intent = sys.argv[1] if len(sys.argv) > 1 else "refactor memory with safety gate"
    print(json.dumps(map_semantic_ontology(intent), indent=2))
