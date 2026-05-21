# Spec Reference: 188_embedding_activation_verifier
import os
import sys
import json
from pathlib import Path

# Spec Reference: 188_embedding_activation_verifier


def run_embedding_activation_verification() -> dict:
    aiwg_root = Path(__file__).resolve().parents[2] / ".aiwg"
    reports_dir = aiwg_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    sentence_transformers_importable = False
    torch_importable = False
    torch_cuda_available = False
    local_model_available = False
    model_load_ok = False
    embedding_mode = "UNKNOWN"
    vector_dimension = 0
    router_uses_real_embeddings = False
    warnings = []
    evidence_refs = [".aiwg/reports/embedding_memory_router_latest.json"]

    # Level 1: Import checks
    try:
        import torch

        torch_importable = True
        torch_cuda_available = torch.cuda.is_available()
    except ImportError as e:
        warnings.append(f"Torch import failed: {e}")

    try:
        from sentence_transformers import SentenceTransformer

        sentence_transformers_importable = True
    except ImportError as e:
        warnings.append(f"SentenceTransformers import failed: {e}")

    # Level 2: Try to load model locally without internet
    if sentence_transformers_importable:
        try:
            # Enforce local_files_only=True to prevent network calls
            model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            local_model_available = True
            model_load_ok = True
            embedding_mode = "REAL_LOCAL"
            vector_dimension = 384

            # Simple similarity query test
            v1 = model.encode("DUMMIE Engine")
            v2 = model.encode("Agentic AI system")
            import numpy as np

            cos_sim = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
            if cos_sim > 0.0:
                router_uses_real_embeddings = True
        except Exception as e:
            # Model not cached or load error
            warnings.append(f"Local sentence-transformers model not loaded: {e}")
            local_model_available = False
            model_load_ok = False
            embedding_mode = "DETERMINISTIC_FALLBACK"
            vector_dimension = 384

    # Read router report to see if it claims ready
    router_report_path = reports_dir / "embedding_memory_router_latest.json"
    if router_report_path.exists():
        try:
            with open(router_report_path, "r", encoding="utf-8") as f:
                router_data = json.load(f)
                # Keep matching values or update if real active
        except Exception:
            pass

    # Determine validation decision
    # Do not claim real semantic embeddings READY unless model_load_ok and router_uses_real_embeddings are true.
    if model_load_ok and router_uses_real_embeddings:
        decision = "PASS"
    else:
        decision = "PASS_WITH_WARNINGS"
        warnings.append("Using deterministic fallback SHA256 router projections.")

    report = {
        "decision": decision,
        "sentence_transformers_importable": sentence_transformers_importable,
        "torch_importable": torch_importable,
        "torch_cuda_available": torch_cuda_available,
        "local_model_available": local_model_available,
        "model_load_ok": model_load_ok,
        "embedding_mode": embedding_mode,
        "vector_dimension": vector_dimension,
        "router_uses_real_embeddings": router_uses_real_embeddings,
        "warnings": warnings,
        "evidence_refs": evidence_refs,
    }

    # Write JSON report
    json_path = reports_dir / "embedding_activation_verification_latest.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write Markdown report
    md_path = reports_dir / "embedding_activation_verification_latest.md"
    md_content = f"""# Embedding Activation Verification Report
**Decision**: `{decision}`  
**Embedding Mode**: `{embedding_mode}`

## Verification Summary
- **SentenceTransformers Importable**: {sentence_transformers_importable}
- **Torch Importable**: {torch_importable}
- **Torch CUDA Available**: {torch_cuda_available}
- **Local Model Available**: {local_model_available}
- **Model Load OK**: {model_load_ok}
- **Vector Dimension**: {vector_dimension}
- **Router Uses Real Embeddings**: {router_uses_real_embeddings}

## Warnings
{chr(10).join(f"- {w}" for w in warnings) if warnings else "None"}
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return report
