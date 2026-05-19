# Spec Reference: 192_embedding_mesh_foundation
import argparse
import sys
from pathlib import Path
from .matrix import StructuralTriageMatrix
from .reporter import StructuralHardeningReporter
from .contracts import RiskLevel


def main(args_list: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DUMMIE Engine - Structural Hardening Triage CLI"
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Root path of the DUMMIE Engine repository"
    )
    parser.add_argument(
        "--write-reports",
        action="store_true",
        help="Whether to write structural triage reports to the .aiwg/reports/ directory"
    )
    parser.add_argument(
        "--max-actions",
        type=int,
        default=50,
        help="Maximum action items to include in top actions list"
    )
    parser.add_argument(
        "--include-low-risk",
        action="store_true",
        help="Includes low risk items in reporting output"
    )
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Exit with non-zero status if any critical-risk items are found"
    )

    args = parser.parse_args(args_list)
    repo_root = Path(args.repo_root).resolve()

    print(f"=== Starting Structural Hardening Triage on {repo_root} ===")
    
    try:
        matrix = StructuralTriageMatrix(str(repo_root))
        report = matrix.analyze()
        
        print("\nTriage Analysis Complete.")
        print(f"Base Commit: {report.base_commit}")
        print(f"Files Analyzed: {report.files_analyzed}")
        print(f"Repository Health Status: {report.repo_health_status}")
        
        print("\nSummary Counts by Structural Class:")
        for cls_name, count in sorted(report.summary_counts.items()):
            print(f"  - {cls_name}: {count}")
            
        high_risk_actions = len(report.top_actions)
        print(f"\nTop Unresolved High-Risk Actions Count: {high_risk_actions}")
        
        if args.write_reports:
            print("\nWriting structural reports to .aiwg/reports/...")
            reporter = StructuralHardeningReporter(str(repo_root))
            written = reporter.write_reports(report, max_actions=args.max_actions)
            print("Successfully wrote reports:")
            print(f"  - JSON: {written['triage_json']}")
            print(f"  - Markdown: {written['triage_md']}")
            print(f"  - Actions JSON: {written['actions_json']}")
            print(f"  - Actions MD: {written['actions_md']}")
            
        if args.fail_on_critical:
            # Check if there are any findings with risk high/critical
            criticals = sum(1 for f in report.findings if f.risk in [RiskLevel.CRITICAL, RiskLevel.HIGH])
            if criticals > 0:
                print(f"\n[ERROR] Found {criticals} high/critical risk items. Failing as requested.")
                return 1
                
        return 0

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Triage failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
