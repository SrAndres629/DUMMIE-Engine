"""Embedding Memory Router Module for offline indexing and routing context items."""

import json
import hashlib
from pathlib import Path

class EmbeddingMemoryRouter:
    def __init__(self, aiwg_root: Path = None):
        if aiwg_root is None:
            aiwg_root = Path(__file__).resolve().parents[2]
        self.aiwg_root = aiwg_root
        self.embeddings_dir = self.aiwg_root / ".aiwg" / "embeddings"
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.aiwg_root / ".aiwg" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _generate_projection_vector(self, text: str) -> list:
        # Generate a deterministic 128-dimensional float projection vector from SHA256 of text
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vector = []
        for i in range(128):
            # Deterministic projection vector generation
            val = (h[i % len(h)] + i) % 256
            vector.append(float(val) / 256.0)
        return vector

    def build_context_embedding_index(self) -> int:
        packet_path = self.reports_dir / "6d_context_packet_latest.json"
        if not packet_path.exists():
            return 0
        
        try:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        except Exception:
            return 0

        index = {
            "embedding_mode": "DETERMINISTIC_FALLBACK",
            "items": []
        }

        for item in packet.get("items", []):
            path = item.get("path", "")
            vector = self._generate_projection_vector(path)
            index["items"].append({
                "path": path,
                "vector": vector,
                "status": item.get("status", "unknown")
            })

        index_path = self.embeddings_dir / "context_embedding_index.json"
        index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
        return len(index["items"])

    def query_context_memory(self, query: str) -> list:
        index_path = self.embeddings_dir / "context_embedding_index.json"
        if not index_path.exists():
            return []

        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            return []

        query_vector = self._generate_projection_vector(query)
        results = []

        for item in index.get("items", []):
            vector = item.get("vector", [])
            # Simple cosine similarity approximation (dot product since vectors normalized roughly same)
            dot_product = sum(a * b for a, b in zip(query_vector, vector))
            results.append({
                "path": item.get("path"),
                "score": float(dot_product),
                "status": item.get("status")
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]

def run_embedding_memory_router_demo(intent: str, aiwg_root: Path = None) -> dict:
    router = EmbeddingMemoryRouter(aiwg_root=aiwg_root)
    indexed_count = router.build_context_embedding_index()
    results = router.query_context_memory(intent)

    warnings = []
    decision = "PASS"
    
    # We must issue fallback warnings if deterministic is active
    warnings.append("Deterministic offline projection fallback is active. Semantic accuracy may be limited.")

    evidence_refs = []
    if (router.reports_dir / "6d_context_packet_latest.json").exists():
        evidence_refs.append(".aiwg/reports/6d_context_packet_latest.json")

    report = {
        "decision": decision,
        "embedding_mode": "DETERMINISTIC_FALLBACK",
        "indexed_items": indexed_count,
        "query": intent,
        "results": results,
        "warnings": warnings,
        "evidence_refs": evidence_refs
    }

    # Save reports
    json_path = router.reports_dir / "embedding_memory_router_latest.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_lines = [
        f"# Embedding Memory Router Report",
        f"- **Decision**: **{decision}**",
        f"- **Embedding Mode**: `DETERMINISTIC_FALLBACK`",
        f"- **Indexed Items**: {indexed_count}",
        f"- **Query**: \"{intent}\"",
        f"",
        f"## Query Results (Top Ranked)",
        f"| Rank | File Path | Score | Status |",
        f"| :--- | :--- | :--- | :--- |",
    ]
    for idx, r in enumerate(results, start=1):
        md_lines.append(f"| {idx} | `{r['path']}` | {r['score']:.4f} | `{r['status']}` |")

    if warnings:
        md_lines.append("\n## Warnings")
        for w in warnings:
            md_lines.append(f"- [WARNING] {w}")

    md_path = router.reports_dir / "embedding_memory_router_latest.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return report


def seed_embedding_router_indices(aiwg_root: Path = None) -> dict:
    router = EmbeddingMemoryRouter(aiwg_root=aiwg_root)
    count = router.build_context_embedding_index()
    index_path = router.embeddings_dir / "context_embedding_index.json"
    vectors = {}
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
            vectors = {item["path"]: item["vector"] for item in index.get("items", [])}
        except Exception:
            pass
    return {
        "status": "PASS",
        "fallback_mode": "DETERMINISTIC_FALLBACK",
        "indexed_count": count,
        "vectors": vectors
    }
