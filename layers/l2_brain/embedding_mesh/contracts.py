from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EmbeddingCapability(str, Enum):
    TEXT_FAST = "TEXT_FAST"
    TEXT_FIDELITY = "TEXT_FIDELITY"
    CODE = "CODE"
    MULTIMODAL = "MULTIMODAL"
    RERANKER = "RERANKER"
    FALLBACK = "FALLBACK"


class ContentType(str, Enum):
    TEXT = "TEXT"
    CODE = "CODE"
    SPEC = "SPEC"
    TEST = "TEST"
    REPORT = "REPORT"
    CONFIG = "CONFIG"
    IMAGE = "IMAGE"
    PDF = "PDF"
    UNKNOWN = "UNKNOWN"


class VectorSpace:
    TEXT_FAST_BGE_SMALL_384 = "text_fast_bge_small_384"
    TEXT_FIDELITY_BGE_M3_1024 = "text_fidelity_bge_m3_1024"
    CODE_LOCAL_768 = "code_local_768"
    MULTIMODAL_CLIP_512 = "multimodal_clip_512"
    FALLBACK_HASH_384 = "fallback_hash_384"


def fallback_vector_space(dimensions: int) -> str:
    return f"fallback_hash_{dimensions}"


def vector_spaces_compatible(left: Optional[str], right: Optional[str]) -> bool:
    if not left or not right:
        return False
    return left == right


class EmbeddingRequest(BaseModel):
    content: str = Field(..., description="The raw string to be vectorized")
    content_type: ContentType = Field(ContentType.UNKNOWN, description="Semantic classification of the content")
    path: Optional[str] = Field(None, description="Optional path to source file")
    language: Optional[str] = Field(None, description="Programming language if applicable")
    capability: Optional[EmbeddingCapability] = Field(None, description="Requested embedding capability")
    locus_x: Optional[str] = Field(None, description="Optional semantic dimension X")
    locus_y: Optional[str] = Field(None, description="Optional semantic dimension Y")
    locus_z: Optional[str] = Field(None, description="Optional semantic dimension Z")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary context metadata")


class EmbeddingResponse(BaseModel):
    vector: List[float] = Field(..., description="Dense numerical representation")
    dimensions: int = Field(..., description="Vector dimensions count")
    model_used: str = Field(..., description="Model identifier")
    capability: EmbeddingCapability = Field(..., description="Actual capability used")
    vector_space: str = Field(..., description="Sovereign vector space naming key")
    normalized: bool = Field(True, description="Whether the vector is unit-normalized")
    degraded: bool = Field(False, description="True if operating under fallback or reduced capacity")
    reason: str = Field("", description="Reason for degraded status if any")
    payload_hash: str = Field(..., description="SHA-256 checksum of the vectorized payload")


class RerankRequest(BaseModel):
    query: str = Field(..., description="Search query")
    candidates: List[Any] = Field(..., description="List of memory items, dicts, or strings")
    top_k: int = Field(5, description="Number of results to return")
    content_type: Optional[ContentType] = Field(None, description="Expected content type")


class RerankMode(str, Enum):
    HYBRID_DETERMINISTIC_FALLBACK = "hybrid_deterministic_fallback"
    HYBRID_REAL_EMBEDDINGS = "hybrid_real_embeddings"
    ML_RERANKER_REAL = "ml_reranker_real"
    BYPASS_VECTOR_SIMILARITY = "bypass_vector_similarity"


class RerankResponse(BaseModel):
    ranked_candidates: List[Dict[str, Any]] = Field(..., description="Candidates with calculated similarity scores")
    model_used: str = Field(..., description="Verification model name")
    degraded: bool = Field(False, description="True if operating under fallback or reduced capacity")
    reason: str = Field("", description="Warning details or fallback explanation")
    ranking_mode: str = Field("hybrid_deterministic_fallback", description="Active ranking mode used")
    semantic_input_degraded: bool = Field(True, description="True if semantic query or candidates are degraded")
    reranker_engine_degraded: bool = Field(True, description="True if motor is deterministic hybrid instead of ML model")
    vector_space: Optional[str] = Field(None, description="Vector space active during comparison")
    weights: Optional[Dict[str, float]] = Field(None, description="Weight distribution used")
    diagnostics: Optional[Dict[str, Any]] = Field(None, description="Diagnostic data of the execution")
