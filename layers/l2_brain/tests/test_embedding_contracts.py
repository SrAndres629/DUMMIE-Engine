import pytest
from pydantic import ValidationError
from layers.l2_brain.domain.embedding_contract import (
    EmbeddingRequest, EmbeddingResponse,
    CompressionRequest, CompressionResponse
)

def test_embedding_request_validation():
    # Valid Request
    req = EmbeddingRequest(text="Hello DUMMIE")
    assert req.text == "Hello DUMMIE"
    assert req.model_name == "BAAI/bge-small-en-v1.5"

    # Missing text should raise ValidationError
    with pytest.raises(ValidationError):
        EmbeddingRequest()

def test_embedding_response_validation():
    resp = EmbeddingResponse(vector=[0.1, 0.2, 0.3], dimensions=3, model_used="test-model")
    assert resp.dimensions == 3
    assert len(resp.vector) == 3

def test_compression_request_defaults():
    req = CompressionRequest(raw_text="Some long text")
    assert req.max_tokens == 4000
    assert req.priority_query is None

def test_compression_response_validation():
    resp = CompressionResponse(compressed_text="Short", tokens_used=1, loss_ratio=0.99)
    assert resp.loss_ratio == 0.99
