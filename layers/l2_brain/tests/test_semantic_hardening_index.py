import os
import json
from layers.l2_brain.embedding_mesh.repo_indexer import RepoIndexer
from layers.l2_brain.embedding_mesh.hardening_matrix import HardeningMatrix
from layers.l2_brain.embedding_mesh.contracts import RerankRequest, ContentType, VectorSpace
from layers.l2_brain.embedding_mesh.reranker import HybridReranker
from layers.l2_brain.embedding_mesh.cli import build_semantic_hardening_index

def test_repo_indexer_and_exclusions():
    # Setup indexer pointed to L2 brain package path to keep it fast
    brain_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    indexer = RepoIndexer(repo_root=brain_root, max_file_bytes=100000)
    
    # Exclude tests and build artifacts
    scan_report = indexer.scan(generate_embeddings=False)
    
    assert scan_report["files_scanned"] > 0
    
    # Assert exclusions
    for f in scan_report["files"]:
        path_lower = f["path"].lower()
        assert ".git" not in path_lower
        assert ".venv" not in path_lower
        assert "node_modules" not in path_lower
        assert "__pycache__" not in path_lower

def test_hardening_matrix_generation():
    # Mock scan report
    mock_scan = {
        "files_scanned": 4,
        "generated_at": "2026-05-18T18:00:00Z",
        "files": [
            {
                "path": "layers/l2_brain/model_router.py",
                "classification": "ACTIVE_CANDIDATE",
                "content_type": ContentType.CODE,
                "language": "python",
                "size_bytes": 1024,
                "sha256": "hash1",
                "capability": "CODE",
                "vector_space": VectorSpace.CODE_LOCAL_768,
                "embedding_degraded": False,
                "embedding_reason": "",
                "embedding": [0.1] * 768,
                "summary": "Cognitive model router module."
            },
            {
                "path": "doc/specs/189_model_router.md",
                "classification": "SPEC",
                "content_type": ContentType.SPEC,
                "language": "markdown",
                "size_bytes": 500,
                "sha256": "hash2",
                "capability": "TEXT_FIDELITY",
                "vector_space": VectorSpace.TEXT_FIDELITY_BGE_M3_1024,
                "embedding_degraded": False,
                "embedding_reason": "",
                "embedding": [0.2] * 1024,
                "summary": "Specification mapping for model router."
            },
            {
                "path": "layers/l2_brain/tests/test_model_router.py",
                "classification": "TEST",
                "content_type": ContentType.TEST,
                "language": "python",
                "size_bytes": 300,
                "sha256": "hash3",
                "capability": "CODE",
                "vector_space": VectorSpace.CODE_LOCAL_768,
                "embedding_degraded": False,
                "embedding_reason": "",
                "embedding": [0.15] * 768,
                "summary": "Unit tests for model router."
            },
            {
                "path": "layers/l2_brain/shadow_module.py",
                "classification": "ACTIVE_CANDIDATE",
                "content_type": ContentType.CODE,
                "language": "python",
                "size_bytes": 600,
                "sha256": "hash4",
                "capability": "CODE",
                "vector_space": VectorSpace.CODE_LOCAL_768,
                "embedding_degraded": False,
                "embedding_reason": "",
                "embedding": [0.05] * 768,
                "summary": "An unreferenced shadow module candidate."
            }
        ]
    }
    
    matrix = HardeningMatrix.generate(mock_scan)
    assert matrix["total_modules"] == 4
    
    records_by_module = {r["module"]: r for r in matrix["records"]}
    
    # 1. model_router.py should be low risk since it has a test and a spec match
    router_rec = records_by_module["layers/l2_brain/model_router.py"]
    assert router_rec["classification"] == "ACTIVE_RUNTIME"
    assert "doc/specs/189_model_router.md" in router_rec["likely_specs"]
    assert "layers/l2_brain/tests/test_model_router.py" in router_rec["likely_tests"]
    assert router_rec["risk"] == "low"
    assert router_rec["recommendation"] == "keep_and_test"
    
    # 2. shadow_module.py should be SHADOW_CANDIDATE and high risk
    shadow_rec = records_by_module["layers/l2_brain/shadow_module.py"]
    assert shadow_rec["classification"] == "SHADOW_CANDIDATE"
    assert shadow_rec["risk"] == "high"
    assert shadow_rec["recommendation"] == "map_to_spec"

def test_hybrid_reranker_and_vector_safety():
    candidates = [
        {
            "text": "The quick brown fox jumps over the lazy dog",
            "path": "src/fox.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "custom_2d",
            "metadata": {"classification": "ACTIVE_RUNTIME"}
        },
        {
            "text": "Baking a delicious chocolate cake with cream",
            "path": "src/cake.py",
            "content_type": ContentType.CODE,
            "embedding": [0.0, 1.0],
            "vector_space": "custom_2d",
            "metadata": {"classification": "ACTIVE_RUNTIME"}
        },
        {
            "text": "Stale legacy component from version 1",
            "path": "src/legacy_component.py",
            "content_type": ContentType.CODE,
            "embedding": [1.0, 0.0],
            "vector_space": "different_space_3d",
            "metadata": {"classification": "LEGACY"}
        }
    ]
    
    req = RerankRequest(
        query="Bake cake",
        candidates=candidates,
        top_k=3,
        content_type=ContentType.CODE
    )
    
    # Vector spaces that are different must not trigger vector similarity or comparison
    resp = HybridReranker.rerank(
        req, 
        query_vector=[0.0, 1.0], 
        query_vector_space="custom_2d"
    )
    
    ranked = resp.ranked_candidates
    assert ranked[0]["candidate"]["path"] == "src/cake.py"
    # cake.py should have highest score because of token overlap ("bake", "cake") AND matching vector
    assert ranked[0]["score"] > ranked[1]["score"]
    
    # legacy_component.py must be penalized heavily due to LEGACY classification
    legacy_rec = [r for r in ranked if r["candidate"]["path"] == "src/legacy_component.py"][0]
    assert legacy_rec["metrics"]["penalty"] == 0.4


def test_report_json_structure(tmp_path):
    repo = tmp_path / "repo"
    (repo / "layers" / "l2_brain").mkdir(parents=True)
    (repo / "doc" / "specs").mkdir(parents=True)
    (repo / "layers" / "l2_brain" / "model_router.py").write_text("def route():\n    return 1\n", encoding="utf-8")
    (repo / "layers" / "l2_brain" / "tests").mkdir(parents=True)
    (repo / "layers" / "l2_brain" / "tests" / "test_model_router.py").write_text(
        "def test_route():\n    assert True\n", encoding="utf-8"
    )
    (repo / "doc" / "specs" / "189_model_router.md").write_text("# model router\n", encoding="utf-8")
    (repo / "README.md").write_text("readme\n", encoding="utf-8")

    build_semantic_hardening_index(str(repo), max_file_bytes=200000, write_reports=True)

    reports_dir = repo / ".aiwg" / "reports"
    index_json = reports_dir / "semantic_repo_index_latest.json"
    matrix_json = reports_dir / "semantic_hardening_matrix_latest.json"
    assert index_json.exists()
    assert matrix_json.exists()

    index_payload = json.loads(index_json.read_text(encoding="utf-8"))
    matrix_payload = json.loads(matrix_json.read_text(encoding="utf-8"))

    assert "files_scanned" in index_payload
    assert "files_indexed" in index_payload
    assert isinstance(index_payload.get("files"), list)

    assert "records" in matrix_payload
    assert isinstance(matrix_payload.get("records"), list)
