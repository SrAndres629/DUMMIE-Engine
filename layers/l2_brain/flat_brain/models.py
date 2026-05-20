"""
[SHIM] flat_brain.models
Redirige estáticamente a los modelos canónicos de L2 Brain para mantener compatibilidad
sin duplicar lógica ni definiciones.
"""
from layers.l2_brain.memory.models import (
    AuthorityLevel,
    IntentType,
    MemoryTemperature,
    SixDimensionalContext,
    AgentIntent,
    MemoryNode4D,
    compute_causal_hash,
    CausalIntegrityVerifier,
    SourceArtifact,
    MemoryTemperatureSignal,
    IntentDraft,
    ConsensusDecision,
    RehydrationManifest
)

__all__ = [
    "AuthorityLevel",
    "IntentType",
    "MemoryTemperature",
    "SixDimensionalContext",
    "AgentIntent",
    "MemoryNode4D",
    "compute_causal_hash",
    "CausalIntegrityVerifier",
    "SourceArtifact",
    "MemoryTemperatureSignal",
    "IntentDraft",
    "ConsensusDecision",
    "RehydrationManifest"
]
