# Spec Reference: 192_embedding_mesh_foundation
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

class HardeningMatrix:
    """
    Builds a module/spec/test/report relation matrix with risk recommendations.
    """

    @staticmethod
    def generate(scan_report: Dict[str, Any]) -> Dict[str, Any]:
        files = scan_report.get("files", [])
        vectors_by_space = _build_vector_index(files, max_candidates_per_space=300)
        specs = [item for item in files if item.get("classification") == "SPEC"]
        tests = [item for item in files if item.get("classification") == "TEST"]
        reports = [item for item in files if item.get("classification") == "REPORT"]

        records: List[Dict[str, Any]] = []
        for file_rec in files:
            module = file_rec["path"]
            matrix_class = _matrix_classification(file_rec)
            likely_specs = _find_likely_specs(file_rec, specs)
            likely_tests = _find_likely_tests(file_rec, tests)
            related_reports = _find_related_reports(file_rec, reports)
            semantic_neighbors = _semantic_neighbors(file_rec, vectors_by_space, limit=3)
            evidence = _build_evidence(file_rec, likely_specs, likely_tests, related_reports)
            risk, recommendation = _risk_and_recommendation(
                matrix_class=matrix_class,
                file_rec=file_rec,
                likely_specs=likely_specs,
                likely_tests=likely_tests,
                evidence=evidence,
            )
            if matrix_class == "ACTIVE_RUNTIME" and risk == "high":
                matrix_class = "SHADOW_CANDIDATE"

            records.append(
                {
                    "module": module,
                    "classification": matrix_class,
                    "likely_specs": likely_specs,
                    "likely_tests": likely_tests,
                    "related_reports": related_reports,
                    "semantic_neighbors": semantic_neighbors,
                    "risk": risk,
                    "recommendation": recommendation,
                    "evidence": evidence,
                }
            )

        counts = Counter(r["classification"] for r in records)
        recommendations = Counter(r["recommendation"] for r in records)
        degraded_embeddings = sum(1 for file_rec in files if file_rec.get("embedding_degraded"))
        high_risk_count = sum(1 for row in records if row.get("risk") == "high")
        medium_risk_count = sum(1 for row in records if row.get("risk") == "medium")

        pack_status = _compute_pack_status(
            files_indexed=scan_report.get("files_indexed", len(files)),
            degraded_embeddings=degraded_embeddings,
        )
        repo_health_status = _compute_repo_health_status(high_risk_count=high_risk_count, medium_risk_count=medium_risk_count)
        semantic_mode = "degraded_semantic_mode" if degraded_embeddings > 0 else "semantic_mode_active"
        index_mode = "deterministic_index_mode" if degraded_embeddings > 0 else "model_index_mode"

        return {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "files_scanned": scan_report.get("files_scanned", len(files)),
            "files_indexed": scan_report.get("files_indexed", len(files)),
            "total_modules": len(records),
            "classification_counts": dict(sorted(counts.items())),
            "recommendation_counts": dict(sorted(recommendations.items())),
            "pack_status": pack_status,
            "repo_health_status": repo_health_status,
            "semantic_mode": semantic_mode,
            "index_mode": index_mode,
            "degraded_embeddings": degraded_embeddings,
            "excluded_files_count": scan_report.get("excluded_files_count", 0),
            "excluded_dirs_count": scan_report.get("excluded_dirs_count", 0),
            "excluded_by_reason": scan_report.get("excluded_by_reason", {}),
            "indexed_first_party_files": scan_report.get("indexed_first_party_files", 0),
            "indexed_legacy_files": scan_report.get("indexed_legacy_files", 0),
            "indexed_generated_files": scan_report.get("indexed_generated_files", 0),
            "indexed_vendor_files": scan_report.get("indexed_vendor_files", 0),
            "records": records,
        }


def _matrix_classification(file_rec: Dict[str, Any]) -> str:
    path = file_rec.get("path", "")
    classification = file_rec.get("classification", "UNKNOWN")
    content_type = str(file_rec.get("content_type", "")).upper()

    if classification == "ACTIVE_CANDIDATE":
        if "/experimental/" in f"/{path}" or "_exp" in Path(path).name:
            return "EXPERIMENTAL"
        return "ACTIVE_RUNTIME"
    if classification == "TEST":
        return "ACTIVE_TEST"
    if classification == "SPEC":
        return "ACTIVE_SPEC"
    if classification == "GENERATED":
        return "GENERATED"
    if classification == "VENDOR":
        return "GENERATED"
    if classification == "LEGACY":
        return "LEGACY"
    if classification == "REPORT":
        return "REPORT"
    if classification == "CONFIG":
        return "CONFIG"
    if content_type == "TEST":
        return "ACTIVE_TEST"
    if content_type == "SPEC":
        return "ACTIVE_SPEC"
    return "UNKNOWN"


def _find_likely_specs(file_rec: Dict[str, Any], specs: List[Dict[str, Any]]) -> List[str]:
    path = file_rec.get("path", "")
    path_base = Path(path).stem.lower()
    path_tokens = set(_normalized_tokens(path_base))

    matches: List[str] = []
    for spec in specs:
        spec_path = spec.get("path", "")
        spec_stem = Path(spec_path).stem.lower()
        spec_tokens = set(_normalized_tokens(spec_stem))

        common = path_tokens.intersection(spec_tokens)
        common = {token for token in common if token not in {"test", "runtime", "spec", "rules", "feature"}}
        if len(common) >= 2:
            matches.append(spec_path)
            continue

        numeric_prefix = re.match(r"^(\d+)", spec_stem)
        if numeric_prefix and numeric_prefix.group(1) in path:
            matches.append(spec_path)

    return sorted(set(matches))[:8]


def _find_likely_tests(file_rec: Dict[str, Any], tests: List[Dict[str, Any]]) -> List[str]:
    if file_rec.get("classification") == "TEST":
        return []

    path = file_rec.get("path", "")
    stem = Path(path).stem
    direct = {f"test_{stem}.py", f"{stem}_test.py"}

    matches: List[str] = []
    for test in tests:
        test_name = Path(test.get("path", "")).name
        if test_name in direct or stem in test_name:
            matches.append(test["path"])

    return sorted(set(matches))[:8]


def _find_related_reports(file_rec: Dict[str, Any], reports: List[Dict[str, Any]]) -> List[str]:
    stem_tokens = set(_normalized_tokens(Path(file_rec.get("path", "")).stem))
    if not stem_tokens:
        return []

    matches: List[str] = []
    for report in reports:
        report_tokens = set(_normalized_tokens(Path(report.get("path", "")).stem))
        overlap = stem_tokens.intersection(report_tokens)
        if len(overlap) >= 1:
            matches.append(report["path"])

    return sorted(set(matches))[:5]


def _build_vector_index(files: List[Dict[str, Any]], max_candidates_per_space: int) -> Dict[str, List[Dict[str, Any]]]:
    by_space: Dict[str, List[Dict[str, Any]]] = {}
    for file_rec in files:
        vector = file_rec.get("embedding") or []
        space = file_rec.get("vector_space")
        if not vector or not space or space == "none":
            continue
        by_space.setdefault(space, [])
        if len(by_space[space]) < max_candidates_per_space:
            by_space[space].append(file_rec)
    return by_space


def _semantic_neighbors(
    file_rec: Dict[str, Any],
    vectors_by_space: Dict[str, List[Dict[str, Any]]],
    limit: int = 3,
) -> List[Dict[str, Any]]:
    source_path = file_rec.get("path")
    source_vector = file_rec.get("embedding") or []
    source_space = file_rec.get("vector_space")
    classification = file_rec.get("classification")
    if not source_vector or not source_space or source_space == "none":
        return []
    if classification not in {"ACTIVE_CANDIDATE", "TEST", "SPEC", "REPORT"}:
        return []

    neighbors: List[Tuple[str, float]] = []
    for other in vectors_by_space.get(source_space, []):
        other_path = other.get("path")
        if other_path == source_path:
            continue

        other_vector = other.get("embedding") or []
        if not other_vector:
            continue
        if len(source_vector) != len(other_vector):
            continue

        dot = sum(a * b for a, b in zip(source_vector, other_vector))
        neighbors.append((other_path, dot))

    neighbors.sort(key=lambda item: item[1], reverse=True)
    return [{"path": path, "similarity": round(score, 4)} for path, score in neighbors[:limit]]


def _build_evidence(
    file_rec: Dict[str, Any],
    likely_specs: List[str],
    likely_tests: List[str],
    related_reports: List[str],
) -> List[str]:
    evidence = ["file_exists"]

    if file_rec.get("language") != "unknown":
        evidence.append("language_detected")
    if file_rec.get("embedding_status") in {"ok", "degraded"}:
        evidence.append("embedded_or_degraded")
    if likely_specs:
        evidence.append("referenced_by_spec")
    if likely_tests:
        evidence.append("referenced_by_test")
    if related_reports:
        evidence.append("referenced_by_report")

    return evidence


def _risk_and_recommendation(
    matrix_class: str,
    file_rec: Dict[str, Any],
    likely_specs: List[str],
    likely_tests: List[str],
    evidence: List[str],
) -> Tuple[str, str]:
    path = file_rec.get("path", "")

    if matrix_class == "ACTIVE_RUNTIME":
        if not likely_tests and not likely_specs:
            return "high", "map_to_spec"
        if not likely_tests:
            return "medium", "needs_test"
        if not likely_specs:
            return "medium", "map_to_spec"
        return "low", "keep_and_test"

    if matrix_class == "ACTIVE_TEST":
        if "test_" in Path(path).name and "referenced_by_test" not in evidence:
            return "medium", "map_to_runtime"
        return "low", "keep_and_test"

    if matrix_class == "ACTIVE_SPEC":
        if not likely_tests:
            return "medium", "needs_test"
        return "low", "keep_and_test"

    if matrix_class == "LEGACY":
        return "medium", "archive_or_delete_later"

    if matrix_class == "GENERATED":
        return "low", "mark_generated"

    if matrix_class == "EXPERIMENTAL":
        return "medium", "needs_import_check"

    if matrix_class == "CONFIG":
        if "shield" in path.lower() or "security" in path.lower():
            return "medium", "needs_security_review"
        return "low", "keep_and_test"

    if matrix_class == "REPORT":
        return "low", "keep_and_test"

    return "medium", "move_to_legacy"


def _normalized_tokens(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.replace("-", "_").lower())


def _compute_pack_status(files_indexed: int, degraded_embeddings: int) -> str:
    if files_indexed <= 0:
        return "FAIL"
    if degraded_embeddings > 0:
        return "PASS_WITH_WARNINGS"
    return "PASS"


def _compute_repo_health_status(high_risk_count: int, medium_risk_count: int) -> str:
    if high_risk_count > 0:
        return "FAIL"
    if medium_risk_count > 0:
        return "PASS_WITH_WARNINGS"
    return "PASS"
