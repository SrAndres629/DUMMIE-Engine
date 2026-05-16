from __future__ import annotations

import importlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


@dataclass
class RestartGateResult:
    decision: str  # PASS|PASS_WITH_WARNINGS|FAIL
    checks: list[dict[str, Any]]
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RestartIntegrationGate:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.repo_root = self.aiwg_root.parent if self.aiwg_root.name == ".aiwg" else self.aiwg_root
        self.reports_root = self.aiwg_root / "reports"

    def run_restart_gate(self, write_report: bool = True) -> RestartGateResult:
        checks: list[dict[str, Any]] = []
        failures: list[str] = []
        warnings: list[str] = []

        # Critical state files
        current_position = self._check_json(
            self.aiwg_root / "evolution" / "current_position.json",
            critical=True,
            checks=checks,
            failures=failures,
            warnings=warnings,
        )
        next_seed = self._check_json(
            self.aiwg_root / "evolution" / "next_phase_seed.json",
            critical=True,
            checks=checks,
            failures=failures,
            warnings=warnings,
        )

        phases = self._check_yaml(
            self.aiwg_root / "evolution" / "phases.yaml",
            critical=True,
            checks=checks,
            failures=failures,
            warnings=warnings,
        )
        phase_graph = self._check_json(
            self.aiwg_root / "evolution" / "phase_dependencies.graph.json",
            critical=True,
            checks=checks,
            failures=failures,
            warnings=warnings,
        )

        if isinstance(current_position, dict) and isinstance(next_seed, dict):
            cp = current_position.get("current_phase")
            nrp = current_position.get("next_required_phase")
            nsp = next_seed.get("next_phase")
            if not cp or not nrp or not nsp:
                failures.append("current_position_or_next_seed_missing_required_fields")
            if nrp != nsp:
                failures.append("next_phase_mismatch_between_current_position_and_next_seed")
            checks.append({"name": "state_alignment", "status": "PASS" if nrp == nsp else "FAIL"})

        if isinstance(phase_graph, dict):
            edges = {(e.get("from"), e.get("to")) for e in phase_graph.get("edges", [])}
            chain = [("P14", "P15"), ("P15", "P16"), ("P16", "P17"), ("P17", "P18")]
            chain_ok = all(edge in edges for edge in chain)
            checks.append({"name": "phase_chain_p14_p18", "status": "PASS" if chain_ok else "FAIL"})
            if not chain_ok:
                failures.append("phase_graph_invalid_for_p14_to_p18_chain")

        # Optional artifacts
        optional_json = [
            ".aiwg/world_model/project_world_model.json",
            ".aiwg/architecture/polyglot_architecture_registry.yaml",
            ".aiwg/reports/spec_coverage_matrix.json",
            ".aiwg/notes/folder_notes_manifest.json",
            ".aiwg/reports/freshness_ledger.json",
            ".aiwg/reports/stale_memory_report.json",
            ".aiwg/reports/context_package_latest.json",
            ".aiwg/reports/context_receipt_latest.json",
            ".aiwg/reports/prompt_cache_summary_latest.json",
        ]
        for rel in optional_json:
            path = self.repo_root / rel
            if rel.endswith(".yaml"):
                self._check_yaml(path, critical=False, checks=checks, failures=failures, warnings=warnings)
            else:
                self._check_json(path, critical=False, checks=checks, failures=failures, warnings=warnings)

        # Critical imports: P10-P13 and P14-P17 runtime modules
        critical_modules = [
            "layers.l2_brain.freshness_ledger",
            "layers.l2_brain.stale_memory_detector",
            "layers.l2_brain.context_package",
            "layers.l2_brain.context_value_scorer",
            "layers.l2_brain.context_quant_runtime",
            "layers.l2_brain.prompt_frame_builder",
            "layers.l2_brain.prompt_cache_ledger",
            "layers.l2_brain.restart_integration_gate",
            "layers.l2_brain.context_efficiency_benchmark",
            "layers.l2_brain.evolution_flywheel_runtime",
        ]
        for module_name in critical_modules:
            try:
                importlib.import_module(module_name)
                checks.append({"name": f"import:{module_name}", "status": "PASS"})
            except Exception as exc:  # pragma: no cover - exercised in simulated test
                checks.append({"name": f"import:{module_name}", "status": "FAIL", "error": str(exc)})
                failures.append(f"critical_module_import_failed:{module_name}")

        decision = "PASS"
        if failures:
            decision = "FAIL"
        elif warnings:
            decision = "PASS_WITH_WARNINGS"

        result = RestartGateResult(
            decision=decision,
            checks=checks,
            failures=sorted(set(failures)),
            warnings=sorted(set(warnings)),
            generated_at=self._utc_now(),
        )

        if write_report:
            self.reports_root.mkdir(parents=True, exist_ok=True)
            out = self.reports_root / "restart_integration_gate_latest.json"
            out.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")

        return result

    def _check_json(
        self,
        path: Path,
        *,
        critical: bool,
        checks: list[dict[str, Any]],
        failures: list[str],
        warnings: list[str],
    ) -> dict[str, Any] | None:
        label = str(path)
        if not path.exists():
            checks.append({"name": f"json:{label}", "status": "MISSING"})
            if critical:
                failures.append(f"missing_critical_json:{label}")
            else:
                warnings.append(f"missing_optional_json:{label}")
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            checks.append({"name": f"json:{label}", "status": "PASS"})
            return data
        except Exception as exc:
            checks.append({"name": f"json:{label}", "status": "FAIL", "error": str(exc)})
            if critical:
                failures.append(f"invalid_critical_json:{label}")
            else:
                warnings.append(f"invalid_optional_json:{label}")
            return None

    def _check_yaml(
        self,
        path: Path,
        *,
        critical: bool,
        checks: list[dict[str, Any]],
        failures: list[str],
        warnings: list[str],
    ) -> Any:
        label = str(path)
        if not path.exists():
            checks.append({"name": f"yaml:{label}", "status": "MISSING"})
            if critical:
                failures.append(f"missing_critical_yaml:{label}")
            else:
                warnings.append(f"missing_optional_yaml:{label}")
            return None
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            checks.append({"name": f"yaml:{label}", "status": "PASS"})
            return data
        except Exception as exc:
            checks.append({"name": f"yaml:{label}", "status": "FAIL", "error": str(exc)})
            if critical:
                failures.append(f"invalid_critical_yaml:{label}")
            else:
                warnings.append(f"invalid_optional_yaml:{label}")
            return None

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")



def run_restart_gate(aiwg_root: str | Path = ".aiwg", write_report: bool = True) -> RestartGateResult:
    gate = RestartIntegrationGate(aiwg_root=aiwg_root)
    return gate.run_restart_gate(write_report=write_report)
