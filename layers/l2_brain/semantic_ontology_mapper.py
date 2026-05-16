
from datetime import datetime, timezone
from typing import Dict, Any

def map_semantic_ontology(intent: str) -> Dict[str, Any]:
    mapping = {
        "refactor": "DEBT", "memory": "MEMORY", "daemon": "RUNTIME",
        "chat": "ENTRYPOINT", "status": "REPORT", "readiness": "CALIBRATION"
    }
    classes = [mapping[kw] for kw in mapping if kw in intent.lower()]
    return {
        "decision": "PASS" if classes else "UNKNOWN",
        "classes": classes or ["UNKNOWN"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
