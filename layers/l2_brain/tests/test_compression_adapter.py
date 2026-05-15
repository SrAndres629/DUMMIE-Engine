import pytest
from layers.l2_brain.domain.embedding_contract import CompressionRequest
from layers.l2_brain.infrastructure.semantic_adapters import LocalContextCompressor

def test_compressor_no_truncation_needed():
    compressor = LocalContextCompressor()
    req = CompressionRequest(raw_text="Hello world, this is a short test.", max_tokens=100)
    
    resp = compressor.compress(req)
    
    assert resp.loss_ratio == 0.0
    assert resp.compressed_text == "Hello world, this is a short test."
    assert resp.tokens_used < 15

def test_compressor_hard_truncation():
    compressor = LocalContextCompressor()
    long_text = "word " * 5000 # Appx 5000 tokens
    req = CompressionRequest(raw_text=long_text, max_tokens=100)
    
    resp = compressor.compress(req)
    
    assert resp.loss_ratio > 0.90 # It should have thrown away most of it
    assert resp.tokens_used == 100
    assert "[CONTEXT TRUNCATED BY TOKEN BUDGET]" in resp.compressed_text
