# Spec Reference: 192_embedding_mesh_foundation
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .contracts import StructuralClass, Recommendation, RiskLevel


class BindingStatus(str, Enum):
    BOUND_ACTIVE_RUNTIME = "BOUND_ACTIVE_RUNTIME"
    BOUND_ACTIVE_TEST = "BOUND_ACTIVE_TEST"
    BOUND_ACTIVE_SPEC = "BOUND_ACTIVE_SPEC"
    MARKED_LEGACY_WITH_EVIDENCE = "MARKED_LEGACY_WITH_EVIDENCE"
    MARKED_GENERATED_WITH_EVIDENCE = "MARKED_GENERATED_WITH_EVIDENCE"
    NEEDS_MANUAL_OWNER = "NEEDS_MANUAL_OWNER"
    DEFERRED_NO_SAFE_ACTION = "DEFERRED_NO_SAFE_ACTION"


class ContractBinding(BaseModel):
    path: str = Field(..., description="File path relative to repository root")
    layer: str = Field(..., description="Repository architectural layer e.g. L0, L1, L2")
    owner_domain: str = Field(..., description="Sovereign domain of logic ownership")
    structural_class: StructuralClass = Field(..., description="Class assigned after contract verification")
    binding_status: BindingStatus = Field(..., description="State of the contract binding")
    spec_refs: List[str] = Field(default_factory=list, description="IDs or paths to associated specifications")
    test_refs: List[str] = Field(default_factory=list, description="Associated unit/integration test files")
    runtime_refs: List[str] = Field(default_factory=list, description="Associated runtime module pathways")
    evidence_refs: List[str] = Field(default_factory=list, description="Traceable physical evidence matching the target")
    action: Recommendation = Field(Recommendation.NO_ACTION, description="Action recommendation after binding")
    risk_before: RiskLevel = Field(RiskLevel.CRITICAL, description="Initial triage risk level")
    risk_after: RiskLevel = Field(..., description="Risk level after applying contract verification evidence")
    confidence: float = Field(1.0, description="Verification confidence factor")
    notes: str = Field("", description="Detailed engineering reasoning notes")


class ContractBindingRegistry:
    def __init__(self):
        self._bindings: Dict[str, ContractBinding] = {}
        self._initialize_registry()

    def _initialize_registry(self):
        # 1. layers/l1_nervous/bootstrap.py
        self._bindings["layers/l1_nervous/bootstrap.py"] = ContractBinding(
            path="layers/l1_nervous/bootstrap.py",
            layer="L1",
            owner_domain="Nervous System Integration",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l2_brain/application/cognitive/use_cases.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Nervous system bootstrap initialization routine. Wired directly to cognitive orchestration."
        )

        # 2. layers/l1_nervous/application/use_cases.py
        self._bindings["layers/l1_nervous/application/use_cases.py"] = ContractBinding(
            path="layers/l1_nervous/application/use_cases.py",
            layer="L1",
            owner_domain="Nervous Application Orchestration",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/bootstrap.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Active usecases of the L1 nervous layer orchestrating daemon processes."
        )

        # 3. layers/l1_nervous/domain/services.py
        self._bindings["layers/l1_nervous/domain/services.py"] = ContractBinding(
            path="layers/l1_nervous/domain/services.py",
            layer="L1",
            owner_domain="Nervous Domain Logic",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/application/use_cases.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Domain services layer containing active cognitive state schemas."
        )

        # 4. layers/l1_nervous/knowledge_adapters.py
        self._bindings["layers/l1_nervous/knowledge_adapters.py"] = ContractBinding(
            path="layers/l1_nervous/knowledge_adapters.py",
            layer="L1",
            owner_domain="Knowledge Integration",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l2_brain/embedding_mesh/router.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Adapters bridging L1 external inputs with L2 cognitive vector representations."
        )

        # 5. layers/l1_nervous/mcp_registry.py
        self._bindings["layers/l1_nervous/mcp_registry.py"] = ContractBinding(
            path="layers/l1_nervous/mcp_registry.py",
            layer="L1",
            owner_domain="MCP Discovery",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l2_brain/embedding_mesh/router.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Local registry managing capabilities and MCP schema binding contracts."
        )

        # 6. layers/l1_nervous/mcp_transport.py
        self._bindings["layers/l1_nervous/mcp_transport.py"] = ContractBinding(
            path="layers/l1_nervous/mcp_transport.py",
            layer="L1",
            owner_domain="MCP Client transport",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/mcp_registry.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Asynchronous MCP client json-rpc sockets transport layer."
        )

        # 7. layers/l1_nervous/repo_guard.py
        self._bindings["layers/l1_nervous/repo_guard.py"] = ContractBinding(
            path="layers/l1_nervous/repo_guard.py",
            layer="L1",
            owner_domain="Repository Governance",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md", "AGENTS.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/application/use_cases.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Repository governance monitor enforcing commit hooks and rules."
        )

        # 8. layers/l1_nervous/runtime_paths.py
        self._bindings["layers/l1_nervous/runtime_paths.py"] = ContractBinding(
            path="layers/l1_nervous/runtime_paths.py",
            layer="L1",
            owner_domain="System Portability",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/bootstrap.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Dynamic configuration paths resolver to guarantee host OS portability."
        )

        # 9. layers/l1_nervous/tools_impl/nervous.py
        self._bindings["layers/l1_nervous/tools_impl/nervous.py"] = ContractBinding(
            path="layers/l1_nervous/tools_impl/nervous.py",
            layer="L1",
            owner_domain="Nervous Skill Tools",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/mcp_registry.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Skill tool executions matching L1 capabilities contracts."
        )

        # 10. layers/l1_nervous/tools_impl/patch_transactions.py
        self._bindings["layers/l1_nervous/tools_impl/patch_transactions.py"] = ContractBinding(
            path="layers/l1_nervous/tools_impl/patch_transactions.py",
            layer="L1",
            owner_domain="Dynamic Patching Transactions",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/tools_impl/nervous.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Atomic database and memory patch transactional isolation boundaries."
        )

        # 11. layers/l1_nervous/utils.py
        self._bindings["layers/l1_nervous/utils.py"] = ContractBinding(
            path="layers/l1_nervous/utils.py",
            layer="L1",
            owner_domain="Nervous Helpers",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l1_nervous/tests/test_l1_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/bootstrap.py"],
            evidence_refs=["IMPORTABLE: verified by test_l1_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="Generic helper functions for binary stream processing."
        )

        # 12. layers/l0_overseer/supervisor.py
        self._bindings["layers/l0_overseer/supervisor.py"] = ContractBinding(
            path="layers/l0_overseer/supervisor.py",
            layer="L0",
            owner_domain="Daemon Process Supervision",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.BOUND_ACTIVE_RUNTIME,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=["layers/l0_overseer/tests/test_l0_contract_imports.py"],
            runtime_refs=["layers/l1_nervous/bootstrap.py"],
            evidence_refs=["IMPORTABLE: verified by test_l0_contract_imports.py"],
            action=Recommendation.KEEP_AND_TEST,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.LOW,
            confidence=1.0,
            notes="System supervisor managing daemon restarts, locking, and sockets."
        )

        # 13. layers/l1_nervous/internal/skill/blueprint.go
        self._bindings["layers/l1_nervous/internal/skill/blueprint.go"] = ContractBinding(
            path="layers/l1_nervous/internal/skill/blueprint.go",
            layer="L1",
            owner_domain="Go Skill Bindings",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.DEFERRED_NO_SAFE_ACTION,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=[],
            runtime_refs=[],
            evidence_refs=["PHYSICAL_EXISTS: compiled skill definition"],
            action=Recommendation.FREEZE_UNTIL_REVIEW,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.HIGH,
            confidence=0.8,
            notes="Go binary definitions of dynamic skill. Toolchain compilation deferred until next phase."
        )

        # 14. layers/l1_nervous/internal/skill/mcp_client.go
        self._bindings["layers/l1_nervous/internal/skill/mcp_client.go"] = ContractBinding(
            path="layers/l1_nervous/internal/skill/mcp_client.go",
            layer="L1",
            owner_domain="Go MCP Gateway",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.DEFERRED_NO_SAFE_ACTION,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=[],
            runtime_refs=[],
            evidence_refs=["PHYSICAL_EXISTS: MCP client definition in Go"],
            action=Recommendation.FREEZE_UNTIL_REVIEW,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.HIGH,
            confidence=0.8,
            notes="Fast Go JSON-RPC implementation for local sidecar daemon. Deferred due to toolchain compilation limits."
        )

        # 15. layers/l1_nervous/internal/skill/types.go
        self._bindings["layers/l1_nervous/internal/skill/types.go"] = ContractBinding(
            path="layers/l1_nervous/internal/skill/types.go",
            layer="L1",
            owner_domain="Go Types Specs",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.DEFERRED_NO_SAFE_ACTION,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=[],
            runtime_refs=[],
            evidence_refs=["PHYSICAL_EXISTS: Go struct schema"],
            action=Recommendation.FREEZE_UNTIL_REVIEW,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.HIGH,
            confidence=0.8,
            notes="Standard definitions of memory nodes used inside the Go gateway client."
        )

        # 16. layers/l1_nervous/sidecar.go
        self._bindings["layers/l1_nervous/sidecar.go"] = ContractBinding(
            path="layers/l1_nervous/sidecar.go",
            layer="L1",
            owner_domain="Go Process Sidecar",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.DEFERRED_NO_SAFE_ACTION,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=[],
            runtime_refs=[],
            evidence_refs=["PHYSICAL_EXISTS: sidecar.go module"],
            action=Recommendation.FREEZE_UNTIL_REVIEW,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.HIGH,
            confidence=0.8,
            notes="Daemon sidecar orchestrator written in Go to communicate with L0-Overseer."
        )

        # 17. layers/l1_nervous/ssh_sandbox_wrapper.sh
        self._bindings["layers/l1_nervous/ssh_sandbox_wrapper.sh"] = ContractBinding(
            path="layers/l1_nervous/ssh_sandbox_wrapper.sh",
            layer="L1",
            owner_domain="Sandbox Execution Shell",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.DEFERRED_NO_SAFE_ACTION,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=[],
            runtime_refs=[],
            evidence_refs=["PHYSICAL_EXISTS: executable shell sandbox wrapper"],
            action=Recommendation.FREEZE_UNTIL_REVIEW,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.HIGH,
            confidence=0.8,
            notes="Executable bash sandbox harness to execute ssh routines securely. Left deferred for security auditing."
        )

        # 18. layers/l0_overseer/lib/overseer/application.ex
        self._bindings["layers/l0_overseer/lib/overseer/application.ex"] = ContractBinding(
            path="layers/l0_overseer/lib/overseer/application.ex",
            layer="L0",
            owner_domain="Elixir App Supervisor",
            structural_class=StructuralClass.ACTIVE_RUNTIME,
            binding_status=BindingStatus.DEFERRED_NO_SAFE_ACTION,
            spec_refs=["doc/specs/103_cognitive_orchestrator.md"],
            test_refs=[],
            runtime_refs=[],
            evidence_refs=["PHYSICAL_EXISTS: Elixir OTP application configuration"],
            action=Recommendation.FREEZE_UNTIL_REVIEW,
            risk_before=RiskLevel.CRITICAL,
            risk_after=RiskLevel.HIGH,
            confidence=0.8,
            notes="Elixir app supervisor specification of the overseer gateway. OTP tree compilation deferred."
        )

    def get_binding(self, path: str) -> Optional[ContractBinding]:
        clean_path = path.replace("\\", "/").strip("/")
        return self._bindings.get(clean_path)

    def get_all_bindings(self) -> List[ContractBinding]:
        return list(self._bindings.values())
