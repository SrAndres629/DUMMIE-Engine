import pytest
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType

def test_six_dimensional_context_creation():
    v = SixDimensionalContext(
        locus_x="domain",
        locus_y="fabrication",
        locus_z="models",
        lamport_t=100,
        authority_a=AuthorityLevel.AGENT,
        intent_i=IntentType.MUTATION
    )
    assert v.locus_x == "domain"
    assert v.immutable_core() == ("domain", "fabrication", "models", 100, "MUTATION")
    
    hash_val = v.compute_context_hash()
    assert isinstance(hash_val, str)
    assert len(hash_val) == 64

def test_six_dimensional_context_validation():
    with pytest.raises(ValueError):
        # intent_i is required
        SixDimensionalContext(
            locus_x="domain",
            locus_y="fabrication",
            locus_z="models",
            lamport_t=100,
            authority_a=AuthorityLevel.AGENT
        )

