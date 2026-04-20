import pytest
from brain.domain.context.models import Vector6D, AuthorityLevel

def test_vector6d_creation():
    v = Vector6D(x=1.0, y=2.0, z=3.0, t=100, w=0.9, a=AuthorityLevel.AGENT)
    assert v.x == 1.0
    assert v.is_highly_relevant() is True
    assert v.immutable_core() == (1.0, 2.0, 3.0, 100)

def test_vector6d_validation():
    with pytest.raises(ValueError):
        # w cannot be > 1.0
        Vector6D(x=1.0, y=2.0, z=3.0, t=100, w=1.5, a=AuthorityLevel.AGENT)
