from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .contracts import Recommendation, RiskLevel, StructuralClass, StructuralFinding


_CODE_EXT = {".py", ".go", ".rs", ".ex", ".exs", ".js", ".ts", ".tsx", ".sh", ".proto", ".c", ".cpp", ".h"}
_CONFIG_NAMES = {"pyproject.toml", "package.json", "go.mod", "go.sum", "mix.exs", ".gitignore", "makefile"}
_CONFIG_EXT = {".toml", ".yaml", ".yml", ".ini", ".cfg", ".env"}


class StructuralClassifier:
    def __init__(self, repo_root: Path | None = None):
        from .bindings import ContractBindingRegistry

        self.repo_root = repo_root or Path.cwd()
        self._bindings = ContractBindingRegistry()

    def classify(self, file_record: Dict[str, Any], evidence: Dict[str, Any]) -> StructuralFinding:
        path = file_record.get("path", "")
        path_lower = path.lower()
        name = Path(path).name
        suffix = Path(path).suffix.lower()

        related_specs = evidence.get("related_specs", [])
        related_tests = evidence.get("related_tests", [])
        related_runtime = evidence.get("related_runtime", [])
        evidence_refs = evidence.get("evidence_refs", [])
        reasons = list(evidence.get("reasons", []))

        current_class = self._from_semantic_class(file_record.get("classification", "UNKNOWN"))

        # Look up in ContractBindingRegistry and apply validation gate.
        from .bindings import BindingStatus

        binding, validation = self._bindings.evaluate(path, self.repo_root, evidence=evidence)
        if binding and validation:
            proposed_class = binding.structural_class
            if validation.resolved_status in {
                BindingStatus.DEFERRED_NO_SAFE_ACTION,
                BindingStatus.NEEDS_MANUAL_OWNER,
                BindingStatus.TOOLCHAIN_MISSING,
                BindingStatus.SMOKE_FAILED,
                BindingStatus.REMAINS_DEFERRED,
                BindingStatus.NEEDS_MANUAL_REVIEW,
            }:
                proposed_class = StructuralClass.SHADOW_CANDIDATE

            if path.endswith((".go", ".ex", ".sh")) and not validation.linked_test_hits:
                if validation.resolved_status not in {BindingStatus.TOOLCHAIN_VALIDATED, BindingStatus.CONTRACT_BOUND, BindingStatus.SMOKE_PASSED}:
                    proposed_class = StructuralClass.SHADOW_CANDIDATE


            reasons_combined = reasons + [
                f"Bound to contract: {binding.notes}",
                f"binding_status={binding.binding_status.value}",
                f"resolved_status={validation.resolved_status.value}",
            ]
            if validation.issues:
                reasons_combined.append(f"binding_issues={','.join(validation.issues)}")

            evidence_combined = (
                evidence_refs
                + binding.evidence_refs
                + [f"valid_specs={validation.valid_spec_refs}", f"valid_tests={validation.valid_test_refs}"]
            )

            return self._make(
                path,
                current_class,
                proposed_class,
                validation.effective_risk,
                validation.effective_recommendation,
                validation.confidence,
                evidence_combined,
                reasons_combined,
                validation.valid_spec_refs,
                validation.valid_test_refs,
                binding.runtime_refs,
                proposed_class != StructuralClass.SHADOW_CANDIDATE and validation.effective_risk in {RiskLevel.LOW, RiskLevel.MEDIUM},
                proposed_class == StructuralClass.SHADOW_CANDIDATE or validation.effective_risk in {RiskLevel.HIGH, RiskLevel.CRITICAL},
            )


        if path.startswith(".aiwg/reports/"):
            return self._make(
                path,
                current_class,
                StructuralClass.REPORT,
                RiskLevel.LOW,
                Recommendation.NO_ACTION,
                0.98,
                evidence_refs,
                reasons + ["report artifact"],
                related_specs,
                related_tests,
                related_runtime,
                True,
                False,
            )

        if self._is_config(path, name, suffix):
            return self._make(
                path,
                current_class,
                StructuralClass.CONFIG,
                RiskLevel.LOW,
                Recommendation.NO_ACTION,
                0.95,
                evidence_refs,
                reasons + ["config/manifest file"],
                related_specs,
                related_tests,
                related_runtime,
                True,
                False,
            )

        if self._is_generated(path_lower, name):
            return self._make(
                path,
                current_class,
                StructuralClass.GENERATED,
                RiskLevel.LOW,
                Recommendation.MARK_GENERATED,
                0.96,
                evidence_refs,
                reasons + ["generated marker/path"],
                related_specs,
                related_tests,
                related_runtime,
                True,
                False,
            )

        if self._is_legacy(path_lower):
            return self._make(
                path,
                current_class,
                StructuralClass.LEGACY,
                RiskLevel.MEDIUM,
                Recommendation.MARK_LEGACY,
                0.95,
                evidence_refs,
                reasons + ["legacy/deprecated path"],
                related_specs,
                related_tests,
                related_runtime,
                False,
                False,
            )

        if self._is_spec(path_lower, name):
            recommendation = Recommendation.KEEP_AND_TEST if (related_runtime or related_tests) else Recommendation.MAP_TO_RUNTIME
            risk = RiskLevel.LOW if recommendation == Recommendation.KEEP_AND_TEST else RiskLevel.MEDIUM
            return self._make(
                path,
                current_class,
                StructuralClass.ACTIVE_SPEC,
                risk,
                recommendation,
                0.92,
                evidence_refs,
                reasons + ["spec location and format"],
                related_specs,
                related_tests,
                related_runtime,
                False,
                recommendation != Recommendation.KEEP_AND_TEST,
            )

        if self._is_test(path_lower, name):
            if related_runtime:
                return self._make(
                    path,
                    current_class,
                    StructuralClass.ACTIVE_TEST,
                    RiskLevel.MEDIUM if not related_specs else RiskLevel.LOW,
                    Recommendation.KEEP_AND_TEST if related_specs else Recommendation.MAP_TO_SPEC,
                    0.90,
                    evidence_refs,
                    reasons + ["test naming/path pattern with runtime links"],
                    related_specs,
                    related_tests,
                    related_runtime,
                    False,
                    False,
                )

            return self._make(
                path,
                current_class,
                StructuralClass.ORPHAN_TEST_CANDIDATE,
                RiskLevel.MEDIUM,
                Recommendation.MAP_TO_RUNTIME,
                0.88,
                evidence_refs,
                reasons + ["test without deterministic runtime linkage"],
                related_specs,
                related_tests,
                related_runtime,
                False,
                True,
            )

        if self._is_experimental(path_lower):
            return self._make(
                path,
                current_class,
                StructuralClass.EXPERIMENTAL,
                RiskLevel.MEDIUM,
                Recommendation.MARK_EXPERIMENTAL,
                0.87,
                evidence_refs,
                reasons + ["experimental/scratch marker"],
                related_specs,
                related_tests,
                related_runtime,
                False,
                True,
            )

        if self._is_runtime_candidate(path_lower, suffix):
            if name == "__init__.py":
                # Avoid false positives for package glue files.
                return self._make(
                    path,
                    current_class,
                    StructuralClass.ACTIVE_RUNTIME,
                    RiskLevel.LOW,
                    Recommendation.NO_ACTION,
                    0.86,
                    evidence_refs,
                    reasons + ["package glue __init__.py under active layer"],
                    related_specs,
                    related_tests,
                    related_runtime,
                    True,
                    False,
                )

            if not related_specs and not related_tests:
                risk = RiskLevel.CRITICAL if path_lower.startswith("layers/l0_") or path_lower.startswith("layers/l1_") else RiskLevel.HIGH
                recommendation = Recommendation.NEEDS_OWNER if risk == RiskLevel.CRITICAL else Recommendation.MAP_TO_SPEC
                return self._make(
                    path,
                    current_class,
                    StructuralClass.SHADOW_CANDIDATE,
                    risk,
                    recommendation,
                    0.84,
                    evidence_refs,
                    reasons + ["runtime candidate missing spec/test linkage"],
                    related_specs,
                    related_tests,
                    related_runtime,
                    False,
                    True,
                )

            if not related_tests:
                return self._make(
                    path,
                    current_class,
                    StructuralClass.ACTIVE_RUNTIME,
                    RiskLevel.MEDIUM,
                    Recommendation.MAP_TO_TEST,
                    0.90,
                    evidence_refs,
                    reasons + ["runtime candidate missing test linkage"],
                    related_specs,
                    related_tests,
                    related_runtime,
                    False,
                    True,
                )

            if not related_specs:
                return self._make(
                    path,
                    current_class,
                    StructuralClass.ACTIVE_RUNTIME,
                    RiskLevel.MEDIUM,
                    Recommendation.MAP_TO_SPEC,
                    0.90,
                    evidence_refs,
                    reasons + ["runtime candidate missing spec linkage"],
                    related_specs,
                    related_tests,
                    related_runtime,
                    False,
                    True,
                )

            return self._make(
                path,
                current_class,
                StructuralClass.ACTIVE_RUNTIME,
                RiskLevel.LOW,
                Recommendation.KEEP_AND_TEST,
                0.93,
                evidence_refs,
                reasons + ["runtime candidate linked to specs and tests"],
                related_specs,
                related_tests,
                related_runtime,
                True,
                False,
            )

        return self._make(
            path,
            current_class,
            StructuralClass.UNKNOWN,
            RiskLevel.MEDIUM,
            Recommendation.FREEZE_UNTIL_REVIEW,
            0.70,
            evidence_refs,
            reasons + ["insufficient structural evidence"],
            related_specs,
            related_tests,
            related_runtime,
            False,
            True,
        )

    @staticmethod
    def _from_semantic_class(value: str) -> StructuralClass:
        mapping = {
            "ACTIVE_RUNTIME": StructuralClass.ACTIVE_RUNTIME,
            "ACTIVE_TEST": StructuralClass.ACTIVE_TEST,
            "ACTIVE_SPEC": StructuralClass.ACTIVE_SPEC,
            "GENERATED": StructuralClass.GENERATED,
            "LEGACY": StructuralClass.LEGACY,
            "CONFIG": StructuralClass.CONFIG,
            "REPORT": StructuralClass.REPORT,
            "SHADOW_CANDIDATE": StructuralClass.SHADOW_CANDIDATE,
            "UNKNOWN": StructuralClass.UNKNOWN,
        }
        return mapping.get(str(value), StructuralClass.UNKNOWN)

    @staticmethod
    def _is_config(path: str, name: str, suffix: str) -> bool:
        return name.lower() in _CONFIG_NAMES or suffix in _CONFIG_EXT or path.startswith(".github/workflows/")

    @staticmethod
    def _is_generated(path_lower: str, name: str) -> bool:
        return (
            "generated" in path_lower
            or "proto/" in path_lower and name.endswith((".pb.go", ".pb.ex"))
            or name.endswith(("_pb2.py", "_pb2_grpc.py", ".pb.go", ".pb.ex"))
        )

    @staticmethod
    def _is_legacy(path_lower: str) -> bool:
        return "legacy" in path_lower or ".deprecated/" in path_lower or "/deprecated/" in path_lower

    @staticmethod
    def _is_spec(path_lower: str, name: str) -> bool:
        return (
            path_lower.startswith("doc/specs/")
            or path_lower.startswith("docs/specs/")
            or name.endswith(".feature")
            or name.endswith(".rules.json")
        )

    @staticmethod
    def _is_test(path_lower: str, name: str) -> bool:
        return (
            "/tests/" in f"/{path_lower}"
            or path_lower.startswith("tests/")
            or name.startswith("test_")
            or name.endswith("_test.py")
            or name.endswith("_test.go")
            or name.endswith("_test.exs")
        )

    @staticmethod
    def _is_experimental(path_lower: str) -> bool:
        markers = ("scratch", "experiment", "playground", "prototype", "mock", "demo")
        return any(marker in path_lower for marker in markers)

    @staticmethod
    def _is_runtime_candidate(path_lower: str, suffix: str) -> bool:
        return path_lower.startswith("layers/") and (suffix in _CODE_EXT or Path(path_lower).name == "__init__.py")

    @staticmethod
    def _make(
        path: str,
        current_class: StructuralClass,
        proposed_class: StructuralClass,
        risk: RiskLevel,
        recommendation: Recommendation,
        confidence: float,
        evidence_refs: list[str],
        reasons: list[str],
        related_specs: list[str],
        related_tests: list[str],
        related_runtime: list[str],
        safe_to_change: bool,
        requires_human_review: bool,
    ) -> StructuralFinding:
        return StructuralFinding(
            path=path,
            current_class=current_class,
            proposed_class=proposed_class,
            risk=risk,
            recommendation=recommendation,
            confidence=confidence,
            evidence_refs=sorted(set(evidence_refs)),
            reasons=sorted(set(reasons)),
            related_specs=sorted(set(related_specs)),
            related_tests=sorted(set(related_tests)),
            related_runtime=sorted(set(related_runtime)),
            safe_to_change=safe_to_change,
            requires_human_review=requires_human_review,
        )
