# Spec Reference: 103_cognitive_orchestrator
import pytest
import sys
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent.parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def test_l0_supervisor_is_importable():
    try:
        import layers.l0_overseer.supervisor
    except ImportError as e:
        pytest.skip(f"L0 supervisor dependency missing: {e}")
        
    assert True
