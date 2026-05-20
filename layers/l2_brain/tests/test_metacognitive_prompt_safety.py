from pathlib import Path


def test_reasoning_hook_does_not_request_private_chain_of_thought():
    source = (Path(__file__).resolve().parents[1] / "flat_brain" / "metacognition" / "reasoning_hooks.py").read_text()

    assert "Chain of Thought" not in source
    assert "Cadena de Razonamiento" not in source
    assert "resumen deliberativo verificable" in source
