
from datetime import datetime, timezone
from typing import Dict, Any, List

def map_semantic_ontology(intent: str) -> Dict[str, Any]:
    mapping = {
        "refactor": "DEBT", 
        "memory": "MEMORY", 
        "daemon": "RUNTIME",
        "chat": "ENTRYPOINT", 
        "status": "REPORT", 
        "readiness": "CALIBRATION",
        "token": "TOKEN_ECONOMY",
        "gate": "SAFETY"
    }
    
    classes = []
    nodes = [{"id": "INTENT", "label": intent, "type": "INTENT"}]
    edges = []
    
    for kw, cls in mapping.items():
        if kw in intent.lower():
            classes.append(cls)
            nodes.append({"id": cls, "label": cls, "type": "CLASS"})
            edges.append({"source": "INTENT", "target": cls, "type": "IS_A"})

    # Hardened Graph Relations
    if "DEBT" in classes and "MEMORY" in classes:
        edges.append({"source": "DEBT", "target": "MEMORY", "type": "DEPENDS_ON"})
    
    if "SAFETY" in classes:
        for cls in classes:
            if cls != "SAFETY":
                edges.append({"source": "SAFETY", "target": cls, "type": "VALIDATES"})

    return {
        "decision": "PASS" if classes else "PASS_WITH_WARNINGS",
        "concepts": [intent],
        "classes": classes or ["UNKNOWN"],
        "ontology_graph": {
            "nodes": nodes,
            "edges": edges
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "warnings": ["No ontology classes matched" if not classes else ""]
    }

if __name__ == "__main__":
    import json
    import sys
    intent = sys.argv[1] if len(sys.argv) > 1 else "refactor memory with safety gate"
    print(json.dumps(map_semantic_ontology(intent), indent=2))
