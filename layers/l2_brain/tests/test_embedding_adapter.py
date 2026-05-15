import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from layers.l2_brain.domain.embedding_contract import EmbeddingRequest
from layers.l2_brain.infrastructure.semantic_adapters import FastEmbedAdapter

@pytest.fixture
def mock_fastembed():
    with patch("layers.l2_brain.infrastructure.semantic_adapters.FastEmbedAdapter._get_model") as mock:
        model_instance = MagicMock()
        # Mock the generator behavior of fastembed.embed()
        # Simulate returning a 384-dimensional numpy array
        fake_vector = np.random.rand(384)
        model_instance.embed.return_value = (v for v in [fake_vector])
        mock.return_value = model_instance
        yield mock

def test_fastembed_adapter_success(mock_fastembed):
    adapter = FastEmbedAdapter()
    req = EmbeddingRequest(text="Agentic Reasoning")
    
    resp = adapter.embed(req)
    
    assert resp.dimensions == 384
    assert len(resp.vector) == 384
    assert resp.model_used == "BAAI/bge-small-en-v1.5"
