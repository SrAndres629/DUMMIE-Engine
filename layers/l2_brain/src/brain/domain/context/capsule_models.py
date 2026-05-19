from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ASTSyntaxNode(BaseModel):
    """Representa la estructura sintáctica de un fragmento de código."""
    file_path: str
    symbol_name: str
    symbol_type: str = Field(..., description="function, class, method, import")
    source_hash: str
    loc: int

class ContextCapsule(BaseModel):
    """Spec 52: Cápsula contextual empaquetada e indexada incrementalmente."""
    capsule_id: str
    target_pack: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    ast_nodes: List[ASTSyntaxNode] = Field(default_factory=list)
    relevance_scores: Dict[str, float] = Field(default_factory=dict)
    token_budget_allocated: int
    compressed_payload_bytes: int

class TokenEconomyPolicy(BaseModel):
    """Política dinámica de gasto e incentivos de tokens."""
    max_input_budget: int
    max_output_budget: int
    reserve_tokens: int
    pressure_factor: float = Field(default=1.0, description="Escala de compresión dinámica")
