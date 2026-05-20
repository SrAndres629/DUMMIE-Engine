from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class PreflightContext(BaseModel):
    """Spec 49: Contexto de pre-ejecución vinculante."""
    head_commit: str = Field(..., description="Commit HEAD actual en Git")
    current_pack: str = Field(..., description="Identificador del pack activo o 'NONE'")
    certainty_score: float = Field(..., ge=0.0, le=1.0)
    is_frozen: bool = Field(default=False)
    metrics_baseline: Dict[str, int] = Field(default_factory=dict)
    active_warnings: List[str] = Field(default_factory=list)

class ExecutionReceipt(BaseModel):
    """Spec 50: Recibo firmado de mutación física del estado."""
    receipt_id: str
    command_executed: str
    exit_code: int
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    causal_witness_hash: str = Field(..., description="SHA-256 de coherencia causal L0-L2")
    state_mutated: bool = False

class PostflightMetrics(BaseModel):
    """Spec 51: Métricas de auditoría post-ejecución."""
    tokens_consumed: int
    elapsed_ms: int
    validation_status: str = Field(..., description="PASSED, PASS_WITH_WARNINGS, or FAILED")
    artifacts_generated: List[str] = Field(default_factory=list)
