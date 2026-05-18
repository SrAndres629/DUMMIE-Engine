import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from layers.l2_brain.embedding_mesh.hardening_matrix import HardeningMatrix
from layers.l2_brain.embedding_mesh.repo_indexer import RepoIndexer


def build_semantic_hardening_index(repo_root: str, max_file_bytes: int, write_reports: bool) -> Dict[str, Any]:
    indexer = RepoIndexer(repo_root=repo_root, max_file_bytes=max_file_bytes)
    scan_report = indexer.scan(generate_embeddings=True)
    matrix_report = HardeningMatrix.generate(scan_report)

    result = {
        "semantic_repo_index": scan_report,
        "semantic_hardening_matrix": matrix_report,
    }

    if write_reports:
        reports_dir = Path(repo_root) / ".aiwg" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        index_json_path = reports_dir / "semantic_repo_index_latest.json"
        matrix_json_path = reports_dir / "semantic_hardening_matrix_latest.json"
        index_md_path = reports_dir / "semantic_repo_index_latest.md"
        matrix_md_path = reports_dir / "semantic_hardening_matrix_latest.md"

        index_json_path.write_text(json.dumps(scan_report, indent=2, ensure_ascii=True), encoding="utf-8")
        matrix_json_path.write_text(json.dumps(matrix_report, indent=2, ensure_ascii=True), encoding="utf-8")

        index_md_path.write_text(_build_index_markdown(scan_report), encoding="utf-8")
        matrix_md_path.write_text(_build_matrix_markdown(scan_report, matrix_report), encoding="utf-8")

    return result


def _build_index_markdown(scan_report: Dict[str, Any]) -> str:
    files = scan_report.get("files", [])
    lines: List[str] = []
    lines.append("# DUMMIE Engine - Semantic Repository Index")
    lines.append("")
    lines.append(f"- generated_at: {scan_report.get('generated_at')}")
    lines.append(f"- files_scanned: {scan_report.get('files_scanned', 0)}")
    lines.append(f"- files_indexed: {scan_report.get('files_indexed', len(files))}")
    lines.append(f"- max_file_bytes: {scan_report.get('max_file_bytes')}")
    lines.append("")
    lines.append("## Indexed Files")

    for file_row in sorted(files, key=lambda row: row.get("path", ""))[:200]:
        lines.append(
            f"- [{file_row.get('classification', 'UNKNOWN')}] {file_row.get('path')} "
            f"| type={file_row.get('content_type')} | cap={file_row.get('capability')} "
            f"| space={file_row.get('vector_space')} | degraded={file_row.get('embedding_degraded')}"
        )

    if len(files) > 200:
        lines.append(f"- ... truncated ({len(files) - 200} files not shown)")

    return "\n".join(lines) + "\n"


def _build_matrix_markdown(scan_report: Dict[str, Any], matrix_report: Dict[str, Any]) -> str:
    records = matrix_report.get("records", [])
    files = scan_report.get("files", [])

    vector_spaces = sorted({row.get("vector_space", "none") for row in files})
    degraded_embeddings = sum(1 for row in files if row.get("embedding_degraded"))
    active_runtime_candidates = sum(1 for row in records if row.get("classification") == "ACTIVE_RUNTIME")
    shadow_candidates = sum(1 for row in records if row.get("classification") == "SHADOW_CANDIDATE")
    generated_candidates = sum(1 for row in records if row.get("classification") == "GENERATED")
    legacy_candidates = sum(1 for row in records if row.get("classification") == "LEGACY")

    orphan_test_candidates = sum(
        1 for row in records if row.get("classification") == "ACTIVE_TEST" and row.get("recommendation") == "map_to_runtime"
    )

    decision = "PASS"
    if any(r.get("risk") == "high" for r in records):
        decision = "FAIL"
    elif degraded_embeddings > 0 or any(r.get("risk") == "medium" for r in records):
        decision = "PASS_WITH_WARNINGS"

    risk_counter = Counter(f"{r.get('risk')}::{r.get('recommendation')}" for r in records)
    top_actions = [
        row
        for row in sorted(
            records,
            key=lambda r: (0 if r.get("risk") == "high" else 1 if r.get("risk") == "medium" else 2, r.get("module", "")),
        )
        if row.get("recommendation") != "keep_and_test"
    ]

    lines: List[str] = []
    lines.append("# DUMMIE Engine - Semantic Hardening Matrix")
    lines.append("")
    lines.append("## Decision")
    lines.append(decision)
    lines.append("")
    lines.append("## Summary counts")
    lines.append(f"- files_scanned: {scan_report.get('files_scanned', 0)}")
    lines.append(f"- files_indexed: {scan_report.get('files_indexed', len(files))}")
    lines.append(f"- degraded_embeddings: {degraded_embeddings}")
    lines.append(f"- vector_spaces_used: {len(vector_spaces)}")
    lines.append(f"- active_runtime_candidates: {active_runtime_candidates}")
    lines.append(f"- shadow_candidates: {shadow_candidates}")
    lines.append(f"- orphan_test_candidates: {orphan_test_candidates}")
    lines.append(f"- generated_candidates: {generated_candidates}")
    lines.append(f"- legacy_candidates: {legacy_candidates}")
    lines.append("")

    lines.append("## Top risks")
    for key, count in risk_counter.most_common(10):
        risk, recommendation = key.split("::", 1)
        lines.append(f"- {risk}: {recommendation} ({count})")
    if not risk_counter:
        lines.append("- none")
    lines.append("")

    lines.append("## Top 20 hardening actions")
    if top_actions:
        for index, action in enumerate(top_actions[:20], start=1):
            lines.append(
                f"{index}. {action.get('recommendation')} | {action.get('module')} "
                f"| risk={action.get('risk')} | class={action.get('classification')}"
            )
    else:
        lines.append("1. keep_and_test | no immediate high-priority actions")
    lines.append("")

    lines.append("## Next recommended phase")
    lines.append("Structural Hardening Pack 2: contract enforcement and targeted cleanup of high/medium-risk modules.")
    lines.append("")

    lines.append("## Explicit limitations")
    lines.append("- Reranker is deterministic hybrid fallback (no ML cross-encoder wired in this phase).")
    lines.append("- Non-TEXT_FAST capabilities are placeholder providers with deterministic fallback.")
    lines.append("- Repo index is JSON-based in this phase; no external vector DB integration.")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DUMMIE semantic repo index + hardening matrix")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--max-file-bytes", type=int, default=200000, help="Maximum file size to index")
    parser.add_argument(
        "--write-reports",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write JSON/MD reports to .aiwg/reports",
    )
    args = parser.parse_args()

    build_semantic_hardening_index(
        repo_root=args.repo_root,
        max_file_bytes=args.max_file_bytes,
        write_reports=args.write_reports,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
