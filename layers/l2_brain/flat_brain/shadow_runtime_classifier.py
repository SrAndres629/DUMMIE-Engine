# Spec: 171_shadow_runtime_classifier
# Spec: DE-V2-L2-171
"""Shadow Runtime Classifier — Spec 171

Classifies all unimported (shadow) python modules into logical operational roles and outputs non-destructive recommended actions.
"""

import json
import os
from datetime import datetime, timezone
import uuid
from pathlib import Path
from typing import Any, Dict, List


class ShadowRuntimeClassifier:
    def __init__(self, root: Path | None = None):
        if root is None:
            env_root = os.environ.get("DUMMIE_ROOT_DIR") or os.environ.get("DUMMIE_ROOT")
            if env_root:
                root = Path(env_root)
            else:
                root = Path(__file__).resolve().parents[2]
        self.root = root.resolve()
        self.aiwg = self.root / ".aiwg"
        self.reports_dir = self.aiwg / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run_classification(self) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        classification_id = f"cla-{uuid.uuid4().hex[:8]}"

        scan_latest_path = self.reports_dir / "whole_body_scan_latest.json"

        if not scan_latest_path.exists():
            return {
                "classification_id": classification_id,
                "timestamp": timestamp,
                "decision": "FAIL",
                "findings": [],
                "warnings": ["No scanner report found."]
            }

        try:
            scan_data = json.loads(scan_latest_path.read_text(encoding="utf-8"))
        except Exception as e:
            return {
                "classification_id": classification_id,
                "timestamp": timestamp,
                "decision": "FAIL",
                "findings": [],
                "warnings": [f"Failed to parse scanner report: {e}"]
            }

        shadow_paths = scan_data.get("findings", {}).get("shadow_modules", [])
        
        findings: List[Dict[str, Any]] = []
        warnings: List[str] = []

        for p_rel in shadow_paths:
            name = Path(p_rel).name
            
            # Non-destructive classification rules
            classification = "needs_manual_review"
            confidence = 0.5
            why_shadow = "No imports detected, not registered as CLI entrypoint, and lacks active specifications."
            recommended_action = "manual_review"

            # CLI Command handlers & Interface entrypoints
            if "cli" in name or "control_plane" in name or "dummie-ctl" in p_rel:
                classification = "cli_entrypoint"
                confidence = 0.95
                why_shadow = "Recognized CLI control surface or entrypoint module."
                recommended_action = "do_not_touch"
            
            # Scripts & interactive scripts
            elif p_rel.startswith("scripts/") or "script" in name:
                classification = "script_entrypoint"
                confidence = 0.9
                why_shadow = "Identified process execution or utility script."
                recommended_action = "ignore"
                
            # Test helper modules
            elif "tests/" in p_rel or "conftest.py" in name or "test_" in name:
                classification = "test_only_support"
                confidence = 0.85
                why_shadow = "Identified as a test fixture or local support module."
                recommended_action = "ignore"

            # Legacy code blocks
            elif "legacy" in p_rel or "backup" in p_rel or "deprecated" in p_rel:
                classification = "legacy_candidate"
                confidence = 0.9
                why_shadow = "Located in a deprecated or legacy directory."
                recommended_action = "archive"

            # Isolated classes/models (Orphan Candidates)
            elif p_rel.startswith("layers/l2_brain/models.py") or "models" in name:
                classification = "dynamic_import_candidate"
                confidence = 0.8
                why_shadow = "Data model or schema class dynamically resolved by reflection."
                recommended_action = "wire"
                
            # Build artifacts
            elif "build" in p_rel or "setup.py" in name:
                classification = "generated_or_build_artifact"
                confidence = 0.95
                why_shadow = "Build system, compilation, or compilation script."
                recommended_action = "ignore"

            # General orphan candidate
            elif p_rel.startswith("layers/"):
                classification = "orphan_candidate"
                confidence = 0.75
                why_shadow = "Active layer component lacking explicit external import."
                recommended_action = "wire"

            finding = {
                "path": p_rel,
                "classification": classification,
                "confidence": confidence,
                "why_shadow": why_shadow,
                "evidence_refs": [".aiwg/reports/whole_body_scan_latest.json"],
                "recommended_action": recommended_action
            }
            findings.append(finding)

        decision = "PASS"
        if len(findings) > 50:
            warnings.append("High volume of shadow modules detected. Recommend priority audit.")
            decision = "PASS_WITH_WARNINGS"

        result = {
            "classification_id": classification_id,
            "timestamp": timestamp,
            "decision": decision,
            "findings": findings,
            "warnings": warnings
        }

        # Write output JSON
        (self.reports_dir / "shadow_runtime_classification_latest.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )

        # Write output Markdown
        self._write_markdown_report(result)

        return result

    def _write_markdown_report(self, result: Dict[str, Any]):
        md = []
        md.append("# DUMMIE Shadow Runtime Classification Report\n")
        md.append(f"**Classification ID:** `{result['classification_id']}`")
        md.append(f"**Timestamp:** {result['timestamp']}\n")
        md.append(f"## Shadow Audit Status: **{result['decision']}**\n")

        md.append("### Shadow Modules Summary")
        md.append(f"- **Total Shadow Modules Audited:** `{len(result['findings'])}`\n")

        md.append("### Non-Destructive Classifications")
        md.append("| Module Path | Classification | Confidence | Recommended Action |")
        md.append("|---|---|---|---|")
        
        # Display top 20 shadow modules
        count = 0
        for f in sorted(result["findings"], key=lambda x: x["confidence"], reverse=True):
            md.append(f"| [{Path(f['path']).name}](file:///{self.root}/{f['path']}) | `{f['classification']}` | `{f['confidence'] * 100}%` | **{f['recommended_action']}** |")
            count += 1
            if count >= 20:
                break
        
        if len(result["findings"]) > 20:
            md.append(f"\n*Showed top 20 of {len(result['findings'])} shadow modules. See JSON report for the full list.*")

        if result["warnings"]:
            md.append("\n### Active Warnings")
            for w in result["warnings"]:
                md.append(f"- [WARNING] {w}")

        (self.reports_dir / "shadow_runtime_classification_latest.md").write_text("\n".join(md), encoding="utf-8")


def run_shadow_runtime_classifier(aiwg_root: Path = None) -> Dict[str, Any]:
    if aiwg_root is None:
        classifier = ShadowRuntimeClassifier()
    else:
        repo_root = aiwg_root.parent if aiwg_root.name == ".aiwg" else aiwg_root
        classifier = ShadowRuntimeClassifier(root=repo_root)
    return classifier.run_classification()


if __name__ == "__main__":
    res = run_shadow_runtime_classifier()
    print(f"Classification complete. Audited: {len(res['findings'])}")
