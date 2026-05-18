from layers.l2_brain.embedding_mesh.contracts import ContentType, EmbeddingCapability
from layers.l2_brain.embedding_mesh.router import EmbeddingRouter

def test_router_code_classification():
    content_type, capability = EmbeddingRouter.route("layers/l2_brain/model_router.py")
    assert content_type == ContentType.CODE
    assert capability == EmbeddingCapability.CODE

    content_type, capability = EmbeddingRouter.route("layers/l0_overseer/main.go")
    assert content_type == ContentType.CODE
    assert capability == EmbeddingCapability.CODE

def test_router_spec_classification():
    content_type, capability = EmbeddingRouter.route("doc/specs/190_full_body_operational_auditor.md")
    assert content_type == ContentType.SPEC
    assert capability in (EmbeddingCapability.TEXT_FAST, EmbeddingCapability.TEXT_FIDELITY)

def test_router_test_classification():
    content_type, capability = EmbeddingRouter.route("layers/l2_brain/tests/test_model_router.py")
    assert content_type == ContentType.TEST
    assert capability == EmbeddingCapability.CODE

def test_router_config_classification():
    content_type, capability = EmbeddingRouter.route("pyproject.toml")
    assert content_type == ContentType.CONFIG
    assert capability == EmbeddingCapability.TEXT_FAST

def test_router_multimodal_classification():
    content_type, capability = EmbeddingRouter.route("doc/diagrams/palace_map.png")
    assert content_type == ContentType.IMAGE
    assert capability == EmbeddingCapability.MULTIMODAL

    content_type, capability = EmbeddingRouter.route("assets/contract.pdf")
    assert content_type == ContentType.PDF
    assert capability == EmbeddingCapability.MULTIMODAL
