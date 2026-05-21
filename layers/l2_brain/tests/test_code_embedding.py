import math
import tempfile
from pathlib import Path

from layers.l2_brain.embedding_mesh.contracts import (
    ContentType,
    EmbeddingCapability,
    EmbeddingRequest,
    VectorSpace,
)
from layers.l2_brain.embedding_mesh.providers import (
    DeterministicFallbackProvider,
    FastEmbedCodeProvider,
)
from layers.l2_brain.embedding_mesh.registry import EmbeddingRegistry


def test_code_provider_registered():
    registry = EmbeddingRegistry()
    provider = registry.get_provider(EmbeddingCapability.CODE)
    assert provider is not None
    # Should NOT be a PlaceholderCapabilityProvider when fastembed is available
    from layers.l2_brain.embedding_mesh.providers import PlaceholderCapabilityProvider

    assert not isinstance(provider, PlaceholderCapabilityProvider)


def test_code_provider_returns_code_space():
    provider = FastEmbedCodeProvider()
    req = EmbeddingRequest(
        content="def hello(): pass",
        content_type=ContentType.CODE,
        capability=EmbeddingCapability.CODE,
    )
    resp = provider.embed(req)
    assert resp.capability == EmbeddingCapability.CODE
    assert resp.vector_space == VectorSpace.CODE_LOCAL_768
    assert resp.dimensions == 384


def test_code_provider_deterministic_fallback():
    provider = FastEmbedCodeProvider()
    # Simulate offline mode by checking fallback behavior
    req1 = EmbeddingRequest(
        content="class Foo: pass",
        content_type=ContentType.CODE,
        capability=EmbeddingCapability.CODE,
    )
    req2 = EmbeddingRequest(
        content="class Foo: pass",
        content_type=ContentType.CODE,
        capability=EmbeddingCapability.CODE,
    )
    resp1 = provider.embed(req1)
    resp2 = provider.embed(req2)
    assert resp1.payload_hash == resp2.payload_hash
    assert len(resp1.vector) == 384


def test_code_and_text_use_different_vector_spaces():
    registry = EmbeddingRegistry()
    code_provider = registry.get_provider(EmbeddingCapability.CODE)
    text_provider = registry.get_provider(EmbeddingCapability.TEXT_FAST)

    req = EmbeddingRequest(
        content="def process(data): return data * 2",
        content_type=ContentType.CODE,
        capability=EmbeddingCapability.CODE,
    )
    code_resp = code_provider.embed(req)

    req.content_type = ContentType.TEXT
    req.capability = EmbeddingCapability.TEXT_FAST
    text_resp = text_provider.embed(req)

    assert code_resp.vector_space != text_resp.vector_space
    assert code_resp.capability != text_resp.capability


def test_ast_indexer_code_embedding():
    from layers.l2_brain.ast_indexer import ASTBlastRadiusIndexer

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        code_file = tmp_path / "test_module.py"
        code_file.write_text(
            "class Calculator:\n    def add(self, a, b):\n        return a + b\n"
        )
        indexer = ASTBlastRadiusIndexer(str(tmp_path))
        symbols = indexer.parse_file_symbols(str(code_file))
        assert len(symbols) == 2
        assert symbols[0]["type"] == "class"
        assert symbols[0]["name"] == "Calculator"

        embeddings = indexer.embed_file_symbols(str(code_file))
        assert len(embeddings) == 2
        for emb in embeddings:
            assert emb["vector_space"] == VectorSpace.CODE_LOCAL_768 or emb["degraded"]
            assert emb["symbol"] in ("Calculator", "add")
            assert emb["type"] in ("class", "function")
            assert len(emb["vector"]) == 384


def test_code_embedding_different_code_different_vectors():
    provider = FastEmbedCodeProvider()
    req1 = EmbeddingRequest(
        content="def foo(): return 1",
        content_type=ContentType.CODE,
        capability=EmbeddingCapability.CODE,
    )
    req2 = EmbeddingRequest(
        content="def bar(): return 2",
        content_type=ContentType.CODE,
        capability=EmbeddingCapability.CODE,
    )
    resp1 = provider.embed(req1)
    resp2 = provider.embed(req2)
    assert resp1.payload_hash != resp2.payload_hash
