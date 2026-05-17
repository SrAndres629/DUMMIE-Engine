"""Whole-Body Scanner, Wiring Matrix, and Shadow Runtime Detector — HEARTBEAT-1

Audits all files in the workspace using local path parsing and import parsing.
Computes a structural completeness score and identifies stale/orphaned assets.
"""

import ast
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Optional


@dataclass
class FileStats:
    path: str
    size_bytes: int
    lines_count: int
    owner_module: str
    mapped_specs: List[str] = field(default_factory=list)
    mapped_tests: List[str] = field(default_factory=list)
    mapped_schemas: List[str] = field(default_factory=list)
    mapped_reports: List[str] = field(default_factory=list)
    imports_from: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    coherence_score: float = 0.0
    status: str = "fresh"  # fresh|stale|deprecated|orphaned

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WholeBodyScanner:
    def __init__(self, root: Path = Path("/home/jorand/Escritorio/DUMMIE Engine")):
        self.root = root.resolve()
        self.aiwg = self.root / ".aiwg"
        self.reports_dir = self.aiwg / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _get_relative(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)

    # ---------------------------------------------------------------------------
    # Import Parsing
    # ---------------------------------------------------------------------------

    def _extract_imports(self, py_path: Path) -> Set[str]:
        """Extract imported module basenames using AST parsing."""
        imports = set()
        try:
            tree = ast.parse(py_path.read_bytes(), filename=str(py_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except Exception:
            # Fallback regex if syntax error or AST parsing fails
            try:
                content = py_path.read_text(encoding="utf-8", errors="ignore")
                for m in re.finditer(r"^\s*(?:import|from)\s+([a-zA-Z0-9_]+)", content, re.M):
                    imports.add(m.group(1))
            except Exception:
                pass
        return imports

    # ---------------------------------------------------------------------------
    # Core Scan
    # ---------------------------------------------------------------------------

    def run_scan(self) -> Dict[str, Any]:
        import os
        import time
        import hashlib
        start_time = time.time()
        py_files: List[Path] = []
        spec_files: List[Path] = []
        schema_files: List[Path] = []
        report_files: List[Path] = []

        # Find assets efficiently using os.walk directory pruning on high-value paths only
        target_dirs = [
            self.root / "layers",
            self.root / "scripts",
            self.root / "doc",
            self.root / "proto",
            self.root / ".aiwg" / "schemas",
            self.root / ".aiwg" / "reports",
        ]
        for t_dir in target_dirs:
            if not t_dir.exists():
                continue
            for root_dir, dirs, files in os.walk(t_dir):
                # Prune directories in place to avoid walking into huge folders
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "target", "deprecated", "build", "_build")]
                for file in files:
                    path = Path(root_dir) / file
                    rel = self._get_relative(path)
                    if path.suffix == ".py":
                        py_files.append(path)
                    elif path.suffix == ".md" and "doc/specs" in rel:
                        spec_files.append(path)
                    elif path.suffix == ".json" and ".aiwg/schemas" in rel:
                        schema_files.append(path)
                    elif (path.suffix in (".json", ".md")) and ".aiwg/reports" in rel:
                        report_files.append(path)

        print(f"DEBUG: Scanned {len(py_files)} Python files, {len(spec_files)} spec files, {len(schema_files)} schema files, {len(report_files)} report files.")

        # In-memory fast lookups
        py_files_set = {self._get_relative(p) for p in py_files}

        # Initialize tracking index
        file_matrix: Dict[str, FileStats] = {}
        for p in py_files:
            rel = self._get_relative(p)
            lines = 0
            try:
                lines = sum(1 for _ in p.open("r", encoding="utf-8", errors="ignore"))
            except Exception:
                pass
            
            # Module owner deduction
            owner = "unknown"
            if len(p.parts) > len(self.root.parts):
                owner = p.parts[len(self.root.parts)]

            file_matrix[rel] = FileStats(
                path=rel,
                size_bytes=p.stat().st_size,
                lines_count=lines,
                owner_module=owner,
            )

        # ---------------------------------------------------------------------------
        # 1. Spec Mapping (Wiring Matrix)
        # ---------------------------------------------------------------------------
        # Parse physical evidence in specs
        for spec_path in spec_files:
            spec_rel = self._get_relative(spec_path)
            content = spec_path.read_text(encoding="utf-8", errors="ignore")
            
            # Extract paths in backticks
            evidence_paths = re.findall(r"`([^`]+)`", content)
            for raw_ev in evidence_paths:
                clean_ev = raw_ev.strip()
                if not clean_ev or " " in clean_ev:
                    continue
                # Normalize path
                target = self.root / clean_ev
                target_rel = self._get_relative(target)
                if target_rel in file_matrix:
                    file_matrix[target_rel].mapped_specs.append(spec_rel)

        # ---------------------------------------------------------------------------
        # 2. Test Mapping (Optimized In-Memory)
        # ---------------------------------------------------------------------------
        for p_rel, stats in file_matrix.items():
            name = Path(p_rel).stem
            # Look for test_foo.py or tests/test_foo.py in py_files_set
            test_patterns = [
                f"test_{name}.py",
                f"tests/test_{name}.py",
                f"layers/l2_brain/tests/test_{name}.py",
            ]
            for pat in test_patterns:
                for test_candidate in py_files_set:
                    if test_candidate.endswith(pat):
                        stats.mapped_tests.append(test_candidate)
            stats.mapped_tests = list(set(stats.mapped_tests))

        # ---------------------------------------------------------------------------
        # 3. Schema & Report Mapping
        # ---------------------------------------------------------------------------
        for p_rel, stats in file_matrix.items():
            name = Path(p_rel).stem
            # Schema mapping
            for sch in schema_files:
                sch_rel = self._get_relative(sch)
                if name in sch.name:
                    stats.mapped_schemas.append(sch_rel)
            # Report mapping
            for rep in report_files:
                rep_rel = self._get_relative(rep)
                if name in rep.name:
                    stats.mapped_reports.append(rep_rel)

        # ---------------------------------------------------------------------------
        # 4. Import Analysis & Dependency Wiring
        # ---------------------------------------------------------------------------
        import_map: Dict[str, Set[str]] = {}
        for p_rel in file_matrix.keys():
            py_abs = self.root / p_rel
            imports = self._extract_imports(py_abs)
            import_map[p_rel] = imports

        for src_rel, imports in import_map.items():
            stats = file_matrix[src_rel]
            # Map imports_from: find other modules in the matrix
            for imp in imports:
                for target_rel in file_matrix.keys():
                    target_name = Path(target_rel).stem
                    if imp == target_name and target_rel != src_rel:
                        stats.imports_from.append(target_rel)
                        file_matrix[target_rel].imported_by.append(src_rel)

            stats.imports_from = sorted(list(set(stats.imports_from)))

        for stats in file_matrix.values():
            stats.imported_by = sorted(list(set(stats.imported_by)))

        # ---------------------------------------------------------------------------
        # 5. Coherence Score & Status Deductions (Shadow Runtime Detection)
        # ---------------------------------------------------------------------------
        shadow_modules: List[str] = []
        orphaned_tests: List[str] = []
        stale_reports: List[str] = []
        unvalidated_specs: List[str] = []

        for p_rel, stats in file_matrix.items():
            # Coherence calculation
            spec_factor = 1.0 if stats.mapped_specs else 0.0
            test_factor = 1.0 if stats.mapped_tests else 0.0
            wiring_factor = 1.0 if (stats.imports_from or stats.imported_by) else 0.5
            
            stats.coherence_score = round((spec_factor * 0.3 + test_factor * 0.3 + wiring_factor * 0.4) * 100, 2)

            # Shadow runtime identification
            is_test_file = "test_" in Path(p_rel).name or "tests/" in p_rel
            is_entrypoint = p_rel in ("scripts/dummie-ctl", "layers/l2_brain/dummie_chat_cli.py", "layers/l2_brain/cli_control_plane.py")
            
            if not stats.imported_by and not is_test_file and not is_entrypoint:
                if not stats.mapped_specs:
                    stats.status = "orphaned"
                    shadow_modules.append(p_rel)
                else:
                    stats.status = "stale"
            elif is_test_file:
                tested_name = Path(p_rel).name.replace("test_", "")
                has_target = any(tested_name in s for s in file_matrix.keys() if s != p_rel)
                if not has_target:
                    stats.status = "orphaned"
                    orphaned_tests.append(p_rel)

        # Unvalidated specs
        for spec_path in spec_files:
            spec_rel = self._get_relative(spec_path)
            has_mapped = any(spec_rel in stats.mapped_specs for stats in file_matrix.values())
            if not has_mapped:
                unvalidated_specs.append(spec_rel)

        # Stale reports
        now = datetime.now(timezone.utc)
        for rep in report_files:
            rep_rel = self._get_relative(rep)
            mtime = datetime.fromtimestamp(rep.stat().st_mtime, timezone.utc)
            age_hours = (now - mtime).total_seconds() / 3600.0
            if age_hours > 24:
                stale_reports.append(rep_rel)

        # Overall systemic coherence score
        active_weights = [stats.coherence_score for stats in file_matrix.values() if stats.status != "orphaned"]
        overall_coherence = round(sum(active_weights) / len(active_weights), 2) if active_weights else 0.0

        # Build output structure
        runtime_seconds = round(time.time() - start_time, 4)
        sorted_paths = sorted(list(file_matrix.keys()))
        paths_str = ",".join(sorted_paths).encode("utf-8")
        reproducibility_hash = hashlib.sha256(paths_str).hexdigest()

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_coherence_score": overall_coherence,
            "profiling_profile": "active_workspace_scan",
            "report_version": "1.1",
            "freshness_timestamp": datetime.now(timezone.utc).isoformat(),
            "runtime_seconds": runtime_seconds,
            "reproducibility_hash": reproducibility_hash,
            "evidence_refs": [".aiwg/reports/whole_body_scan_latest.json"],
            "metrics": {
                "total_python_files": len(file_matrix),
                "total_spec_files": len(spec_files),
                "total_schema_files": len(schema_files),
                "total_report_files": len(report_files),
                "shadow_modules_count": len(shadow_modules),
                "orphaned_tests_count": len(orphaned_tests),
                "stale_reports_count": len(stale_reports),
                "unvalidated_specs_count": len(unvalidated_specs),
            },
            "findings": {
                "shadow_modules": sorted(shadow_modules),
                "orphaned_tests": sorted(orphaned_tests),
                "stale_reports": sorted(stale_reports),
                "unvalidated_specs": sorted(unvalidated_specs),
            },
            "matrix": {path: stats.to_dict() for path, stats in sorted(file_matrix.items())}
        }

        # Write output JSON
        (self.reports_dir / "whole_body_scan_latest.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )

        # Generate markdown report
        self._write_markdown_report(result, spec_files, schema_files)

        return result

    def _write_markdown_report(self, result: Dict[str, Any], specs: List[Path], schemas: List[Path]):
        md = []
        md.append("# DUMMIE Whole-Body Scan Coherence Report\n")
        md.append(f"**Execution Timestamp:** {result['timestamp']}\n")
        md.append(f"## Systemic Coherence Score: `{result['overall_coherence_score']}%`\n")

        md.append("### Summary Metrics")
        md.append("| Metric | Count |")
        md.append("|---|---|")
        metrics = result["metrics"]
        md.append(f"| Python Modules Scanned | {metrics['total_python_files']} |")
        md.append(f"| Specifications Scanned | {metrics['total_spec_files']} |")
        md.append(f"| JSON Schemas Scanned | {metrics['total_schema_files']} |")
        md.append(f"| Reports Scanned | {metrics['total_report_files']} |")
        md.append(f"| Mapped Shadow Modules | **{metrics['shadow_modules_count']}** |")
        md.append(f"| Orphaned Test Files | **{metrics['orphaned_tests_count']}** |")
        md.append(f"| Stale Reports (>24h) | **{metrics['stale_reports_count']}** |")
        md.append(f"| Unvalidated Specifications | **{metrics['unvalidated_specs_count']}** |")
        md.append("\n")

        # Findings details
        md.append("### Active Anomalies (Shadow Runtime)")
        findings = result["findings"]
        
        md.append("#### Mapped Shadow Modules (Unimported / Unmapped)")
        if findings["shadow_modules"]:
            for f in findings["shadow_modules"]:
                md.append(f"- [{Path(f).name}](file:///{self.root}/{f})")
        else:
            md.append("- *None detected.*")
        md.append("\n")

        md.append("#### Orphaned Test Files")
        if findings["orphaned_tests"]:
            for f in findings["orphaned_tests"]:
                md.append(f"- [{Path(f).name}](file:///{self.root}/{f})")
        else:
            md.append("- *None detected.*")
        md.append("\n")

        md.append("#### Stale Reports (>24h)")
        if findings["stale_reports"]:
            for f in findings["stale_reports"]:
                md.append(f"- [{Path(f).name}](file:///{self.root}/{f})")
        else:
            md.append("- *None detected.*")
        md.append("\n")

        md.append("#### Unvalidated Specifications (0 Mapped Physical Assets)")
        if findings["unvalidated_specs"]:
            for f in findings["unvalidated_specs"]:
                md.append(f"- [{Path(f).name}](file:///{self.root}/{f})")
        else:
            md.append("- *None detected.*")
        md.append("\n")

        # Top 10 lowest coherence files
        md.append("### Lowest Coherence Modules (Priority Repairs)")
        md.append("| Module | Coherence | Specs | Tests | Status |")
        md.append("|---|---|---|---|---|")
        
        sorted_matrix = sorted(result["matrix"].values(), key=lambda x: x["coherence_score"])
        count = 0
        for item in sorted_matrix:
            if "test_" in item["path"] or "tests/" in item["path"]:
                continue
            specs_count = len(item["mapped_specs"])
            tests_count = len(item["mapped_tests"])
            md.append(f"| [{Path(item['path']).name}](file:///{self.root}/{item['path']}) | `{item['coherence_score']}%` | {specs_count} | {tests_count} | {item['status']} |")
            count += 1
            if count >= 10:
                break

        (self.reports_dir / "whole_body_scan_latest.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    scanner = WholeBodyScanner()
    res = scanner.run_scan()
    print(f"Scan complete. Coherence score: {res['overall_coherence_score']}%")
