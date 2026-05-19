# Spec Reference: 192_embedding_mesh_foundation
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .contracts import Recommendation, RiskLevel, StructuralClass


class BindingStatus(str, Enum):
    BOUND_ACTIVE_RUNTIME = "BOUND_ACTIVE_RUNTIME"
    BOUND_ACTIVE_TEST = "BOUND_ACTIVE_TEST"
    BOUND_ACTIVE_SPEC = "BOUND_ACTIVE_SPEC"
    MARKED_LEGACY_WITH_EVIDENCE = "MARKED_LEGACY_WITH_EVIDENCE"
    MARKED_GENERATED_WITH_EVIDENCE = "MARKED_GENERATED_WITH_EVIDENCE"
    NEEDS_MANUAL_OWNER = "NEEDS_MANUAL_OWNER"
    DEFERRED_NO_SAFE_ACTION = "DEFERRED_NO_SAFE_ACTION"
    TOOLCHAIN_VALIDATED = "TOOLCHAIN_VALIDATED"
    TOOLCHAIN_MISSING = "TOOLCHAIN_MISSING"
    SMOKE_PASSED = "SMOKE_PASSED"
    SMOKE_FAILED = "SMOKE_FAILED"
    CONTRACT_BOUND = "CONTRACT_BOUND"
    REMAINS_DEFERRED = "REMAINS_DEFERRED"
    NEEDS_MANUAL_REVIEW = "NEEDS_MANUAL_REVIEW"



class ContractBinding(BaseModel):
    path: str = Field(..., description="File path relative to repository root")
    layer: str = Field(..., description="Repository architectural layer e.g. L0, L1, L2")
    owner_domain: str = Field(..., description="Sovereign domain of logic ownership")
    structural_class: StructuralClass = Field(..., description="Class assigned after contract verification")
    binding_status: BindingStatus = Field(..., description="State of the contract binding")
    spec_refs: List[str] = Field(default_factory=list, description="Associated specifications")
    test_refs: List[str] = Field(default_factory=list, description="Associated unit/integration tests")
    runtime_refs: List[str] = Field(default_factory=list, description="Associated runtime module pathways")
    evidence_refs: List[str] = Field(default_factory=list, description="Traceable physical evidence")
    action: Recommendation = Field(Recommendation.NO_ACTION, description="Action recommendation after binding")
    risk_before: RiskLevel = Field(RiskLevel.CRITICAL, description="Initial triage risk level")
    risk_after: RiskLevel = Field(..., description="Target risk after contract verification")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Verification confidence factor")
    notes: str = Field("", description="Detailed engineering reasoning notes")


class BindingValidation(BaseModel):
    path: str
    resolved_status: BindingStatus
    effective_risk: RiskLevel
    effective_recommendation: Recommendation
    confidence: float = Field(..., ge=0.0, le=1.0)
    valid_spec_refs: List[str] = Field(default_factory=list)
    valid_test_refs: List[str] = Field(default_factory=list)
    valid_runtime_refs: List[str] = Field(default_factory=list)
    missing_spec_refs: List[str] = Field(default_factory=list)
    missing_test_refs: List[str] = Field(default_factory=list)
    missing_runtime_refs: List[str] = Field(default_factory=list)
    direct_spec_hits: List[str] = Field(default_factory=list)
    scoped_spec_hits: List[str] = Field(default_factory=list)
    linked_test_hits: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)


_RISK_ORDER = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.CRITICAL: 3,
}


def _max_risk(a: RiskLevel, b: RiskLevel) -> RiskLevel:
    return a if _RISK_ORDER[a] >= _RISK_ORDER[b] else b


def _ref_exists(repo_root: Path, ref: str) -> bool:
    ref_path = (repo_root / ref).resolve()
    try:
        return ref_path.exists() and ref_path.is_file()
    except Exception:
        return False


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


class ContractBindingRegistry:
    def __init__(self):
        self._bindings: Dict[str, ContractBinding] = {}
        self._initialize_registry()

    def _initialize_registry(self):
        l1_specs = [
            "doc/specs/L1_Nervous/15_mcp_sidecar_isolation.md",
            "doc/specs/L1_Nervous/16_mcp_dynamic_gateway.md",
            "doc/specs/L1_Nervous/41_layer_handshake_protocol.md",
            "doc/specs/L1_Nervous/44_pervasive_channel_adapters.md",
        ]
        l0_specs = [
            "doc/specs/L0_Overseer/03_polyglot_architecture.md",
            "doc/specs/L0_Overseer/05_orchestration_stack_and_glue.md",
            "doc/specs/L0_Overseer/11_monorepo_structure.md",
        ]

        runtime_py_tests = [
            "layers/l1_nervous/tests/test_l1_contract_imports.py",
        ]

        self._bindings["layers/l1_nervous/bootstrap.py"] = ContractBinding(
            path="layers/l1_nervous/bootstrap.py",
            layer="L1",
            owner_domain="Nervous System Integration",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=l1_specs,
            test_refs=runtime_py_tests,
            runtime_refs=["layers/l1_nervous/application/use_cases.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.88,
            notes="L1 bootstrap runtime boundary with optional path fallback logic.",
        )

        self._bindings["layers/l1_nervous/application/use_cases.py"] = ContractBinding(
            path="layers/l1_nervous/application/use_cases.py",
            layer="L1",
            owner_domain="Nervous Application Orchestration",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=l1_specs,
            test_refs=runtime_py_tests,
            runtime_refs=["layers/l1_nervous/domain/services.py", "layers/l1_nervous/bootstrap.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.88,
            notes="Use case orchestration glue for L1 tool operations.",
        )

        self._bindings["layers/l1_nervous/domain/services.py"] = ContractBinding(
            path="layers/l1_nervous/domain/services.py",
            layer="L1",
            owner_domain="Nervous Domain Logic",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=l1_specs,
            test_refs=runtime_py_tests,
            runtime_refs=["layers/l1_nervous/application/use_cases.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.86,
            notes="Domain service contract used by L1 use-cases.",
        )

        self._bindings["layers/l1_nervous/knowledge_adapters.py"] = ContractBinding(
            path="layers/l1_nervous/knowledge_adapters.py",
            layer="L1",
            owner_domain="Knowledge Integration",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=l1_specs,
            test_refs=[
                "layers/l1_nervous/tests/test_l1_contract_imports.py",
                "layers/l1_nervous/tests/test_obsidian_knowledge_adapter.py",
            ],
            runtime_refs=["layers/l1_nervous/application/use_cases.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.84,
            notes="Knowledge adapter path remains active but has import-shape debt (top-level models import).",
        )

        self._bindings["layers/l1_nervous/mcp_registry.py"] = ContractBinding(
            path="layers/l1_nervous/mcp_registry.py",
            layer="L1",
            owner_domain="MCP Discovery",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=l1_specs,
            test_refs=runtime_py_tests,
            runtime_refs=["layers/l1_nervous/mcp_transport.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.88,
            notes="Registry runtime component for MCP server catalog.",
        )

        self._bindings["layers/l1_nervous/mcp_transport.py"] = ContractBinding(
            path="layers/l1_nervous/mcp_transport.py",
            layer="L1",
            owner_domain="MCP Client Transport",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=l1_specs,
            test_refs=runtime_py_tests,
            runtime_refs=["layers/l1_nervous/mcp_registry.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.88,
            notes="Transport implementation for stdio-based MCP communication.",
        )

        self._bindings["layers/l1_nervous/repo_guard.py"] = ContractBinding(
            path="layers/l1_nervous/repo_guard.py",
            layer="L1",
            owner_domain="Repository Governance",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=[
                "doc/specs/130_trusted_workstation_mode.md",
                "doc/specs/111_spec_coverage_gate.md",
                *l1_specs,
            ],
            test_refs=runtime_py_tests,
            runtime_refs=["layers/l1_nervous/application/use_cases.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.83,
            notes="Repo governance helper; requires stronger direct spec anchoring.",
        )

        self._bindings["layers/l1_nervous/runtime_paths.py"] = ContractBinding(
            path="layers/l1_nervous/runtime_paths.py",
            layer="L1",
            owner_domain="System Portability",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=[
                "doc/specs/L0_Overseer/47_path_normalization.md",
                *l1_specs,
            ],
            test_refs=[
                "layers/l1_nervous/tests/test_l1_contract_imports.py",
                "layers/l1_nervous/tests/test_runtime_contracts.py",
            ],
            runtime_refs=["layers/l1_nervous/bootstrap.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.90,
            notes="Deterministic runtime path resolver with dedicated tests.",
        )

        self._bindings["layers/l1_nervous/tools_impl/nervous.py"] = ContractBinding(
            path="layers/l1_nervous/tools_impl/nervous.py",
            layer="L1",
            owner_domain="Nervous Skill Tools",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.DEFERRED_NO_SAFE_ACTION,
            spec_refs=[
                "doc/specs/L1_Nervous/16_mcp_dynamic_gateway.md",
                "doc/specs/L1_Nervous/44_local_reasoning_gateway.md",
            ],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/mcp_registry.py"],
            evidence_refs=["FILE_EXISTS", "OPTIONAL_DEPENDENCY_REQUIRED:mcp"],
            action=Recommendation.FREEZE_UNTIL_REVIEW,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.HIGH,
            confidence=0.76,
            notes="Depends on optional 'mcp' package; import contract must remain deferred.",
        )

        self._bindings["layers/l1_nervous/tools_impl/patch_transactions.py"] = ContractBinding(
            path="layers/l1_nervous/tools_impl/patch_transactions.py",
            layer="L1",
            owner_domain="Dynamic Patching Transactions",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=l1_specs,
            test_refs=runtime_py_tests,
            runtime_refs=["layers/l1_nervous/tools_impl/nervous.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.82,
            notes="Patch transaction helper with import-only coverage.",
        )

        self._bindings["layers/l1_nervous/utils.py"] = ContractBinding(
            path="layers/l1_nervous/utils.py",
            layer="L1",
            owner_domain="Nervous Helpers",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=l1_specs,
            test_refs=runtime_py_tests,
            runtime_refs=["layers/l1_nervous/bootstrap.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.86,
            notes="Utility module for atomic file operations.",
        )

        self._bindings["layers/l0_overseer/supervisor.py"] = ContractBinding(
            path="layers/l0_overseer/supervisor.py",
            layer="L0",
            owner_domain="Daemon Process Supervision",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=l0_specs,
            test_refs=["layers/l0_overseer/tests/test_l0_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/bootstrap.py"],
            evidence_refs=["FILE_EXISTS", "IMPORTABLE"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.MEDIUM,
            confidence=0.87,
            notes="Python supervisor process contract at L0 boundary.",
        )

        deferred_runtime = [
            "layers/l1_nervous/internal/skill/blueprint.go",
            "layers/l1_nervous/internal/skill/mcp_client.go",
            "layers/l1_nervous/internal/skill/types.go",
            "layers/l1_nervous/sidecar.go",
            "layers/l1_nervous/ssh_sandbox_wrapper.sh",
            "layers/l0_overseer/lib/overseer/application.ex",
        ]
        for path in deferred_runtime:
            layer = "L0" if path.startswith("layers/l0_") else "L1"
            owner = "Polyglot Runtime Surface" if layer == "L1" else "Overseer OTP Runtime"
            specs = l0_specs if layer == "L0" else [
                "doc/specs/L1_Nervous/15_mcp_sidecar_isolation.md",
                "doc/specs/L1_Nervous/16_mcp_dynamic_gateway.md",
                "doc/specs/L1_Nervous/41_layer_handshake_protocol.md",
            ]
            self._bindings[path] = ContractBinding(
                path=path,
                layer=layer,
                owner_domain=owner,
                structural_class=StructuralClass.ACTIVE_RUNTIME,
                binding_status=BindingStatus.DEFERRED_NO_SAFE_ACTION,
                spec_refs=specs,
                test_refs=[],
                runtime_refs=[],
                evidence_refs=["FILE_EXISTS", "POLYGLOT_TOOLCHAIN_NOT_VERIFIED"],
                action=Recommendation.FREEZE_UNTIL_REVIEW,
                risk_before=RiskLevel.CRITICAL,
                risk_after=RiskLevel.HIGH,
                confidence=0.72,
                notes="Polyglot runtime without deterministic compile/test evidence in this phase.",
            )

    def get_binding(self, path: str) -> Optional[ContractBinding]:
        clean_path = path.replace("\\", "/").strip("/")
        return self._bindings.get(clean_path)

    def get_all_bindings(self) -> List[ContractBinding]:
        return list(self._bindings.values())

    def evaluate(
        self,
        path: str,
        repo_root: Path,
        evidence: Optional[Dict[str, object]] = None,
    ) -> Tuple[Optional[ContractBinding], Optional[BindingValidation]]:
        binding = self.get_binding(path)
        if not binding:
            return None, None
        return binding, self._validate(binding, repo_root, evidence or {})

    def _validate(self, binding: ContractBinding, repo_root: Path, evidence: Dict[str, object]) -> BindingValidation:
        valid_specs = [ref for ref in binding.spec_refs if _ref_exists(repo_root, ref)]
        valid_tests = [ref for ref in binding.test_refs if _ref_exists(repo_root, ref)]
        valid_runtime = [ref for ref in binding.runtime_refs if _ref_exists(repo_root, ref)]

        missing_specs = sorted(set(binding.spec_refs) - set(valid_specs))
        missing_tests = sorted(set(binding.test_refs) - set(valid_tests))
        missing_runtime = sorted(set(binding.runtime_refs) - set(valid_runtime))

        direct_spec_hits: List[str] = []
        scoped_spec_hits: List[str] = []
        layer_prefix = "/".join(binding.path.split("/")[:2])
        for spec in valid_specs:
            text = _safe_read_text(repo_root / spec).lower()
            if not text:
                continue
            if binding.path.lower() in text or Path(binding.path).name.lower() in text:
                direct_spec_hits.append(spec)
            elif layer_prefix.lower() in text:
                scoped_spec_hits.append(spec)

        linked_test_hits: List[str] = []
        module_name = binding.path.replace("/", ".")
        if module_name.endswith(".py"):
            module_name = module_name[:-3]
        filename = Path(binding.path).name
        stem = Path(binding.path).stem
        for test in valid_tests:
            text = _safe_read_text(repo_root / test)
            if not text:
                continue
            lowered = text.lower()
            if module_name in text or filename in text or stem.lower() in lowered:
                linked_test_hits.append(test)

        evidence_refs = set(str(v) for v in evidence.get("evidence_refs", []) if isinstance(v, str))
        has_importable_evidence = "IMPORTABLE" in evidence_refs
        py_file = binding.path.endswith(".py")

        # Check polyglot ledger first for risk & status calibration
        ledger_path = repo_root / ".aiwg" / "reports" / "structural_polyglot_toolchain_ledger_latest.json"
        polyglot_entry = None
        if ledger_path.exists():
            try:
                import json
                with open(ledger_path, "r", encoding="utf-8") as f:
                    ledger_data = json.load(f)
                    entries = ledger_data if isinstance(ledger_data, list) else ledger_data.get("entries", [])
                    for entry in entries:
                        if entry.get("path") == binding.path:
                            polyglot_entry = entry
                            break
            except Exception:
                pass

        resolved_status = binding.binding_status
        effective_risk = binding.risk_after
        effective_recommendation = binding.action
        issues: List[str] = []

        if polyglot_entry:
            decision = str(polyglot_entry.get("binding_decision", "REMAINS_DEFERRED"))
            risk_after = str(polyglot_entry.get("risk_after", RiskLevel.HIGH.value))
            observed_result = str(polyglot_entry.get("observed_result", "")).lower()
            evidence_command = str(polyglot_entry.get("evidence_command", "")).strip()

            decision_is_positive = decision in {
                BindingStatus.TOOLCHAIN_VALIDATED.value,
                BindingStatus.CONTRACT_BOUND.value,
                BindingStatus.SMOKE_PASSED.value,
            }
            has_success_signal = any(token in observed_result for token in ("pass", "passed", "success", "succeeded", "ok"))

            if decision_is_positive and (not evidence_command or not has_success_signal):
                resolved_status = BindingStatus.REMAINS_DEFERRED
                effective_risk = RiskLevel.HIGH
                effective_recommendation = Recommendation.FREEZE_UNTIL_REVIEW
                issues.append("polyglot_ledger_overclaim_without_executable_success")
            else:
                try:
                    resolved_status = BindingStatus(decision)
                except Exception:
                    resolved_status = BindingStatus.NEEDS_MANUAL_REVIEW
                    issues.append("invalid_binding_decision_in_ledger")
                try:
                    effective_risk = RiskLevel(risk_after)
                except Exception:
                    effective_risk = RiskLevel.HIGH
                    issues.append("invalid_risk_after_in_ledger")

            if decision == BindingStatus.TOOLCHAIN_MISSING.value:
                issues.append(f"toolchain_missing:{polyglot_entry.get('required_toolchain')}")
            if decision == BindingStatus.SMOKE_FAILED.value:
                issues.append("smoke_failed")

            # Add dynamic evidence refs
            evidence_refs.add(f"POLYGLOT_TOOLCHAIN:{polyglot_entry.get('required_toolchain')}")
            evidence_refs.add(f"PROBE:{decision}")

        if not _ref_exists(repo_root, binding.path):
            resolved_status = BindingStatus.NEEDS_MANUAL_OWNER
            effective_risk = RiskLevel.CRITICAL
            effective_recommendation = Recommendation.NEEDS_OWNER
            issues.append("binding target does not exist")

        if missing_specs:
            issues.append(f"missing_spec_refs:{len(missing_specs)}")
        if missing_tests:
            issues.append(f"missing_test_refs:{len(missing_tests)}")
        if missing_runtime:
            issues.append(f"missing_runtime_refs:{len(missing_runtime)}")

        has_strong_spec = bool(direct_spec_hits)
        has_scoped_spec = bool(scoped_spec_hits)
        has_linked_tests = bool(linked_test_hits)

        if py_file and not has_importable_evidence:
            issues.append("missing_importable_evidence")

        if binding.binding_status == BindingStatus.BOUND_ACTIVE_RUNTIME:
            if has_strong_spec and has_linked_tests and (has_importable_evidence or not py_file):
                effective_risk = _max_risk(binding.risk_after, RiskLevel.MEDIUM)
                effective_recommendation = Recommendation.KEEP_AND_TEST
            elif (has_scoped_spec or has_strong_spec) and has_linked_tests:
                effective_risk = _max_risk(binding.risk_after, RiskLevel.MEDIUM)
                effective_recommendation = Recommendation.MAP_TO_SPEC if not has_strong_spec else Recommendation.KEEP_AND_TEST
            elif has_linked_tests and not (has_scoped_spec or has_strong_spec):
                effective_risk = _max_risk(binding.risk_after, RiskLevel.HIGH)
                effective_recommendation = Recommendation.MAP_TO_SPEC
                issues.append("no_valid_spec_link")
            elif (has_scoped_spec or has_strong_spec) and not has_linked_tests:
                effective_risk = _max_risk(binding.risk_after, RiskLevel.HIGH)
                effective_recommendation = Recommendation.MAP_TO_TEST
                issues.append("no_linked_test_evidence")
            else:
                resolved_status = BindingStatus.NEEDS_MANUAL_OWNER
                effective_risk = RiskLevel.CRITICAL
                effective_recommendation = Recommendation.NEEDS_OWNER
                issues.append("runtime binding lacks spec/test linkage")

        if binding.binding_status == BindingStatus.DEFERRED_NO_SAFE_ACTION:
            if polyglot_entry:
                if resolved_status in {BindingStatus.TOOLCHAIN_VALIDATED, BindingStatus.CONTRACT_BOUND, BindingStatus.SMOKE_PASSED}:
                    effective_recommendation = Recommendation.KEEP_AND_TEST
                else:
                    effective_recommendation = Recommendation.FREEZE_UNTIL_REVIEW
            else:
                effective_recommendation = Recommendation.FREEZE_UNTIL_REVIEW
                if has_scoped_spec or has_strong_spec:
                    effective_risk = _max_risk(binding.risk_after, RiskLevel.HIGH)
                else:
                    effective_risk = RiskLevel.CRITICAL
                    resolved_status = BindingStatus.NEEDS_MANUAL_OWNER
                    issues.append("deferred binding lacks spec ownership")


        confidence = binding.confidence
        if missing_specs:
            confidence -= 0.10
        if missing_tests and binding.binding_status == BindingStatus.BOUND_ACTIVE_RUNTIME:
            confidence -= 0.10
        if py_file and not has_importable_evidence:
            confidence -= 0.15
        if not has_linked_tests and binding.binding_status == BindingStatus.BOUND_ACTIVE_RUNTIME:
            confidence -= 0.10
        if not (has_scoped_spec or has_strong_spec):
            confidence -= 0.10
        confidence = max(0.40, min(1.0, confidence))

        return BindingValidation(
            path=binding.path,
            resolved_status=resolved_status,
            effective_risk=effective_risk,
            effective_recommendation=effective_recommendation,
            confidence=confidence,
            valid_spec_refs=valid_specs,
            valid_test_refs=valid_tests,
            valid_runtime_refs=valid_runtime,
            missing_spec_refs=missing_specs,
            missing_test_refs=missing_tests,
            missing_runtime_refs=missing_runtime,
            direct_spec_hits=direct_spec_hits,
            scoped_spec_hits=scoped_spec_hits,
            linked_test_hits=linked_test_hits,
            issues=sorted(set(issues)),
        )
