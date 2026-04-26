from typing import Any

from golden_path import generate_golden_path as build_golden_path
from runtime_guards import GuardInput, evaluate_runtime_guards
from sdd_governance import (
    ChangeRequest,
    EvidencePacket,
    admit_change,
    compile_spec_document,
)


class SDDToolService:
    def evaluate_change_admission(
        self,
        files: list[str],
        intent: str,
        parent_spec_ids: list[str],
        specs: list[dict[str, str]],
        evidence: list[dict[str, Any]],
        risk: str = "medium",
    ) -> dict[str, Any]:
        spec_nodes = [
            compile_spec_document(item["path"], item["text"])
            for item in specs
            if "path" in item and "text" in item
        ]
        evidence_packets = [
            EvidencePacket(
                evidence_id=item["evidence_id"],
                claim=item.get("claim", ""),
                kind=item.get("kind", "unknown"),
                refs=item.get("refs", []),
                verified=bool(item.get("verified", False)),
            )
            for item in evidence
            if "evidence_id" in item
        ]
        decision = admit_change(
            ChangeRequest(
                change_id="l1-request",
                files=files,
                intent=intent,
                parent_spec_ids=parent_spec_ids,
                evidence_ids=[item.evidence_id for item in evidence_packets],
                risk=risk,
            ),
            spec_nodes,
            evidence_packets,
        )
        return decision.__dict__

    def generate_golden_path(
        self,
        spec_id: str,
        approved: bool,
        target_module: str,
    ) -> dict[str, Any]:
        return build_golden_path(spec_id, approved, target_module).__dict__

    def evaluate_runtime_guard(
        self,
        provider_ready: bool,
        memory_locked: bool,
        parent_spec_approved: bool,
        l3_policy: str,
    ) -> dict[str, Any]:
        return evaluate_runtime_guards(
            GuardInput(
                provider_ready=provider_ready,
                memory_locked=memory_locked,
                parent_spec_approved=parent_spec_approved,
                l3_policy=l3_policy,
            )
        ).__dict__


def register_sdd_tools(mcp, use_cases):
    service = SDDToolService()

    @mcp.tool()
    async def sdd_evaluate_change_admission(
        files: list[str],
        intent: str,
        parent_spec_ids: list[str],
        specs: list[dict[str, str]],
        evidence: list[dict[str, Any]],
        risk: str = "medium",
    ) -> str:
        return str(
            service.evaluate_change_admission(
                files=files,
                intent=intent,
                parent_spec_ids=parent_spec_ids,
                specs=specs,
                evidence=evidence,
                risk=risk,
            )
        )

    @mcp.tool()
    async def sdd_generate_golden_path(
        spec_id: str,
        approved: bool,
        target_module: str,
    ) -> str:
        return str(service.generate_golden_path(spec_id, approved, target_module))

    @mcp.tool()
    async def sdd_evaluate_runtime_guard(
        provider_ready: bool,
        memory_locked: bool,
        parent_spec_approved: bool,
        l3_policy: str,
    ) -> str:
        return str(
            service.evaluate_runtime_guard(
                provider_ready=provider_ready,
                memory_locked=memory_locked,
                parent_spec_approved=parent_spec_approved,
                l3_policy=l3_policy,
            )
        )
