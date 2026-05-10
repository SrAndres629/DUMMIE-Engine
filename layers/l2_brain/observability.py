from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class SystemHealth(BaseModel):
    status: str # HEALTHY, DEGRADED, PANIC
    active_sagas: int
    circuit_breakers_open: List[str]
    uptime: float

class SagaStateUpdate(BaseModel):
    transaction_id: str
    current_step: str
    status: str
    timestamp: str = datetime.now().isoformat()

def get_skin_telemetry_contract():
    """Retorna el esquema esperado por la capa L6."""
    return {
        "health_check_path": "/health",
        "ws_stream_path": "/ws/orchestration/updates",
        "payload_types": ["SagaStateUpdate", "SystemHealth"]
    }
