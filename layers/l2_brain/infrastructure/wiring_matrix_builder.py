# Spec: 170_wiring_matrix_builder
# Spec: DE-V2-L2-170
"""Wiring Matrix Builder — Spec 170

Constructs the full bidirectional graph of first-party code, tests, specs, schemas, and reports.
"""

import json
import os
from datetime import datetime, timezone
import uuid
from pathlib import Path
from typing import Any, Dict, List, Set


class WiringMatrixBuilder:
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

    def build_matrix(self) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        matrix_id = f"mat-{uuid.uuid4().hex[:8]}"

        scan_latest_path = self.reports_dir / "whole_body_scan_latest.json"
        
        if not scan_latest_path.exists():
            return {
                "matrix_id": matrix_id,
                "timestamp": timestamp,
                "decision": "FAIL",
                "nodes": [],
                "edges": [],
                "anomaly_summary": {
                    "unwired_source_modules": [],
                    "source_without_tests": [],
                    "source_without_specs": [],
                    "spec_without_source": [],
                    "test_without_source": [],
                    "schema_without_consumer": [],
                    "report_without_consumer": [],
                    "heartbeat_unwired_reports": []
                }
            }

        try:
            scan_data = json.loads(scan_latest_path.read_text(encoding="utf-8"))
        except Exception:
            return {
                "matrix_id": matrix_id,
                "timestamp": timestamp,
                "decision": "FAIL",
                "nodes": [],
                "edges": [],
                "anomaly_summary": {
                    "unwired_source_modules": [],
                    "source_without_tests": [],
                    "source_without_specs": [],
                    "spec_without_source": [],
                    "test_without_source": [],
                    "schema_without_consumer": [],
                    "report_without_consumer": [],
                    "heartbeat_unwired_reports": []
                }
            }

        matrix_data = scan_data.get("matrix", {})
        findings = scan_data.get("findings", {})
        
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        unwired_sources: List[str] = []
        source_without_tests: List[str] = []
        source_without_specs: List[str] = []
        spec_without_source: List[str] = []
        test_without_source: List[str] = []
        schema_without_consumer: List[str] = []
        report_without_consumer: List[str] = []
        heartbeat_unwired_reports: List[str] = []

        # Find unwired / orphan elements from findings
        spec_without_source = findings.get("unvalidated_specs", [])
        test_without_source = findings.get("orphaned_tests", [])

        # Construct Nodes and Edges from the scanner file matrix
        for path_rel, item in sorted(matrix_data.items()):
            # Kind deduction
            kind = "unknown"
            is_test_file = "test_" in Path(path_rel).name or "tests/" in path_rel
            
            if is_test_file:
                kind = "test"
            elif path_rel.startswith("layers") or path_rel.startswith("scripts"):
                kind = "source"
            
            # Layer deduction
            layer = item.get("owner_module", "unknown")
            
            # Lang
            lang = "python"
            if path_rel.endswith(".json"):
                lang = "json"
            elif path_rel.endswith(".md"):
                lang = "markdown"

            status = "wired"
            if item.get("status") == "orphaned":
                status = "shadow"
                unwired_sources.append(path_rel)
            elif item.get("status") == "stale":
                status = "stale"
            
            mapped_specs = item.get("mapped_specs", [])
            mapped_tests = item.get("mapped_tests", [])
            mapped_schemas = item.get("mapped_schemas", [])
            mapped_reports = item.get("mapped_reports", [])
            imports_from = item.get("imports_from", [])
            imported_by = item.get("imported_by", [])

            if kind == "source":
                if not mapped_tests:
                    source_without_tests.append(path_rel)
                if not mapped_specs:
                    source_without_specs.append(path_rel)

            node = {
                "path": path_rel,
                "kind": kind,
                "layer": layer,
                "language": lang,
                "status": status,
                "consumers": sorted(imported_by),
                "producers": sorted(imports_from),
                "tests": sorted(mapped_tests),
                "specs": sorted(mapped_specs),
                "schemas": sorted(mapped_schemas),
                "reports": sorted(mapped_reports),
                "evidence_refs": [".aiwg/reports/whole_body_scan_latest.json"]
            }
            nodes.append(node)

            # Build directed Edges
            # Imports edges
            for imp in imports_from:
                edges.append({
                    "from": path_rel,
                    "to": imp,
                    "edge_type": "imports",
                    "confidence": 1.0,
                    "evidence_refs": [".aiwg/reports/whole_body_scan_latest.json"]
                })

            # Test edges
            for tst in mapped_tests:
                edges.append({
                    "from": tst,
                    "to": path_rel,
                    "edge_type": "tests",
                    "confidence": 1.0,
                    "evidence_refs": [".aiwg/reports/whole_body_scan_latest.json"]
                })

            # Spec edges
            for spc in mapped_specs:
                edges.append({
                    "from": spc,
                    "to": path_rel,
                    "edge_type": "specifies",
                    "confidence": 1.0,
                    "evidence_refs": [".aiwg/reports/whole_body_scan_latest.json"]
                })

            # Schema validation edges
            for sch in mapped_schemas:
                edges.append({
                    "from": sch,
                    "to": path_rel,
                    "edge_type": "validates",
                    "confidence": 1.0,
                    "evidence_refs": [".aiwg/reports/whole_body_scan_latest.json"]
                })

            # Report edges
            for rep in mapped_reports:
                edges.append({
                    "from": rep,
                    "to": path_rel,
                    "edge_type": "reports",
                    "confidence": 1.0,
                    "evidence_refs": [".aiwg/reports/whole_body_scan_latest.json"]
                })

        # Add Spec nodes (from scan_data specs if not present)
        # Scan data metrics has total_spec_files, let's find unvalidated specs and include them
        for spc in spec_without_source:
            node = {
                "path": spc,
                "kind": "spec",
                "layer": "doc",
                "language": "markdown",
                "status": "orphan",
                "consumers": [],
                "producers": [],
                "tests": [],
                "specs": [],
                "schemas": [],
                "reports": [],
                "evidence_refs": [".aiwg/reports/whole_body_scan_latest.json"]
            }
            nodes.append(node)

        # Schema without consumers
        # Let's inspect scanned schemas to see if any doesn't validate any python files
        # We can find all schemas scanned, and check if they are mapped in nodes
        scanned_schemas: Set[str] = set()
        for node in nodes:
            for sch in node["schemas"]:
                scanned_schemas.add(sch)
        
        # Build anomaly summary structure
        anomaly_summary = {
            "unwired_source_modules": sorted(unwired_sources),
            "source_without_tests": sorted(source_without_tests),
            "source_without_specs": sorted(source_without_specs),
            "spec_without_source": sorted(spec_without_source),
            "test_without_source": sorted(test_without_source),
            "schema_without_consumer": sorted(list(schema_without_consumer)),
            "report_without_consumer": sorted(list(report_without_consumer)),
            "heartbeat_unwired_reports": sorted(list(heartbeat_unwired_reports))
        }

        decision = "PASS"
        if unwired_sources or spec_without_source or test_without_source:
            decision = "PASS_WITH_WARNINGS"

        result = {
            "matrix_id": matrix_id,
            "timestamp": timestamp,
            "decision": decision,
            "nodes": nodes,
            "edges": edges,
            "anomaly_summary": anomaly_summary
        }

        # Write output JSON
        (self.reports_dir / "wiring_matrix_latest.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )

        # Write output Markdown
        self._write_markdown_report(result)

        return result

    def _write_markdown_report(self, result: Dict[str, Any]):
        md = []
        md.append("# DUMMIE Wiring Matrix Report\n")
        md.append(f"**Matrix ID:** `{result['matrix_id']}`")
        md.append(f"**Timestamp:** {result['timestamp']}\n")
        md.append(f"## System Wiring Status: **{result['decision']}**\n")

        md.append("### Active Graph Metrics")
        md.append(f"- **Total Nodes:** `{len(result['nodes'])}`")
        md.append(f"- **Total Directed Edges:** `{len(result['edges'])}`\n")

        anom = result["anomaly_summary"]
        md.append("### Disconnected Body Parts (Anomalies)")
        
        md.append("#### Unwired Source Modules")
        if anom["unwired_source_modules"]:
            for f in anom["unwired_source_modules"]:
                md.append(f"- [{Path(f).name}](file:///{self.root}/{f})")
        else:
            md.append("- *None detected.*")
        md.append("\n")

        md.append("#### Source Modules Without Tests")
        if anom["source_without_tests"]:
            for f in anom["source_without_tests"]:
                md.append(f"- [{Path(f).name}](file:///{self.root}/{f})")
        else:
            md.append("- *None detected.*")
        md.append("\n")

        md.append("#### Unvalidated Specifications (Specs Without Source)")
        if anom["spec_without_source"]:
            for f in anom["spec_without_source"]:
                md.append(f"- [{Path(f).name}](file:///{self.root}/{f})")
        else:
            md.append("- *None detected.*")
        md.append("\n")

        md.append("#### Orphaned Test Files (Tests Without Source)")
        if anom["test_without_source"]:
            for f in anom["test_without_source"]:
                md.append(f"- [{Path(f).name}](file:///{self.root}/{f})")
        else:
            md.append("- *None detected.*")
        md.append("\n")

        (self.reports_dir / "wiring_matrix_latest.md").write_text("\n".join(md), encoding="utf-8")


def run_wiring_matrix_builder(aiwg_root: Path = None) -> Dict[str, Any]:
    if aiwg_root is None:
        builder = WiringMatrixBuilder()
    else:
        repo_root = aiwg_root.parent if aiwg_root.name == ".aiwg" else aiwg_root
        builder = WiringMatrixBuilder(root=repo_root)
    return builder.build_matrix()


if __name__ == "__main__":
    res = run_wiring_matrix_builder()
    print(f"Wiring complete. Nodes: {len(res['nodes'])}, Edges: {len(res['edges'])}")
