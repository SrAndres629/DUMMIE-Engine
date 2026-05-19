from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dummie.aiwg import DummieAiwgIntegration
from dummie.config import DummieConfig
from dummie.guardrails import DummieRepoGuard, write_repo_guard_report
from dummie.memory import DummieMemory
from dummie.providers import DummieProviderRegistry
from dummie.session import DummieSessionManager
from dummie.strategic_partner import DummieStrategicPartner
from layers.l2_brain.business_goal_model import create_goal_memory_entry


@dataclass
class DummieEngineStatus:
    decision: str
    preflight: dict[str, Any]
    providers: dict[str, dict[str, Any]]
    root_dir: str
    aiwg_dir: str
    repo_guard: dict[str, Any]
    memory_status: dict[str, Any]
    next_recommended_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "preflight": self.preflight,
            "providers": self.providers,
            "root_dir": self.root_dir,
            "aiwg_dir": self.aiwg_dir,
            "repo_guard": self.repo_guard,
            "memory_status": self.memory_status,
            "next_recommended_action": self.next_recommended_action,
        }


@dataclass
class DummieAdviceResponse:
    goal_type: str
    strategic_questions: list[str]
    tool_opportunities: list[dict[str, Any]]
    roadmap: list[dict[str, Any]]
    advice: dict[str, Any]
    creator_profile: dict[str, Any]
    business_intake: dict[str, Any]
    receipt: dict[str, Any]
    raw_data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_type": self.goal_type,
            "strategic_questions": self.strategic_questions,
            "tool_opportunities": self.tool_opportunities,
            "roadmap": self.roadmap,
            "advice": self.advice,
            "creator_profile": self.creator_profile,
            "business_intake": self.business_intake,
            "receipt": self.receipt,
        }


class DummieEngine:
    def __init__(self):
        self.config = DummieConfig()
        self.session = DummieSessionManager()
        self.providers = DummieProviderRegistry()
        self.aiwg = DummieAiwgIntegration()
        self.partner = DummieStrategicPartner()
        self.memory = DummieMemory()
        self.repo_guard = DummieRepoGuard()

    @classmethod
    def load(cls) -> "DummieEngine":
        return cls()

    def status(self) -> DummieEngineStatus:
        preflight = self.aiwg.run_preflight()
        providers_status = self.providers.get_providers_status(live_check=True)
        repo_guard_model = self.repo_guard.evaluate()
        repo_guard = repo_guard_model.to_dict()
        write_repo_guard_report(repo_guard_model)
        memory_status = self.memory.status()

        decision = "PASS"
        if preflight.get("status") != "PASS" or repo_guard.get("decision") != "PASS":
            decision = "FAIL"

        next_action = "run_dummie_advise_for_active_goal"
        if repo_guard.get("decision") == "FAIL":
            next_action = "clean_blocked_context_killers_before_commit"

        status = DummieEngineStatus(
            decision=decision,
            preflight=preflight,
            providers=providers_status,
            root_dir=str(self.config.root_dir),
            aiwg_dir=str(self.config.aiwg_dir),
            repo_guard=repo_guard,
            memory_status=memory_status,
            next_recommended_action=next_action,
        )

        payload = status.to_dict()
        self.aiwg.write_report("provider_status_latest.json", {
            "decision": "PASS",
            "providers": providers_status,
        })
        self.aiwg.write_report("sovereign_cli_latest.json", payload)
        self.aiwg.write_receipt("status", status.decision, payload)

        return status

    def advise(self, goal_statement: str) -> DummieAdviceResponse:
        runtime_payload = self.partner.advise(goal_statement)

        entry = create_goal_memory_entry(goal_statement)
        self.memory.append_goal(entry.to_dict())

        self.session.record_episode(
            query=goal_statement,
            intent="advise",
            answer=f"goal_type={runtime_payload.get('goal_classification', {}).get('goal_type', 'unknown')}",
            decision="PASS",
            evidence_refs=[
                ".aiwg/identity/goal_memory.yaml",
                ".aiwg/reports/strategic_partner_runtime_latest.json",
            ],
        )

        receipt = self.aiwg.write_receipt(
            "advise",
            "PASS",
            {
                "goal": goal_statement,
                "goal_classification": runtime_payload.get("goal_classification", {}),
            },
        )

        runtime_payload["receipt"] = receipt
        self.aiwg.write_report("business_goal_intake_latest.json", runtime_payload)
        self.aiwg.write_report("strategic_partner_runtime_latest.json", runtime_payload)
        self.aiwg.write_report("pack_s1_sovereign_cli_strategic_partner_runtime.json", runtime_payload)

        self.aiwg.write_markdown_report(
            "pack_s1_sovereign_cli_strategic_partner_runtime.md",
            _build_pack_markdown(runtime_payload),
        )

        return DummieAdviceResponse(
            goal_type=runtime_payload.get("goal_classification", {}).get("goal_type", "unknown"),
            strategic_questions=runtime_payload.get("strategic_questions", []),
            tool_opportunities=runtime_payload.get("tool_opportunities", []),
            roadmap=runtime_payload.get("roadmap", []),
            advice=runtime_payload.get("advice", {}),
            creator_profile=runtime_payload.get("creator_profile", {}),
            business_intake=runtime_payload.get("business_intake", {}),
            receipt=runtime_payload.get("receipt", {}),
            raw_data=runtime_payload,
        )


def _build_pack_markdown(payload: dict[str, Any]) -> str:
    goal_type = payload.get("goal_classification", {}).get("goal_type", "unknown")
    lines = [
        "# PACK S1 Strategic Partner Runtime",
        "",
        f"- Goal type: `{goal_type}`",
        f"- Creator: `{payload.get('creator_profile', {}).get('name', 'unknown')}`",
        "",
        "## Strategic Questions",
    ]
    for question in payload.get("strategic_questions", []):
        lines.append(f"- {question}")
    lines.extend(["", "## Tool Opportunities"])
    for tool in payload.get("tool_opportunities", []):
        lines.append(f"- {tool.get('name')}: {tool.get('description')}")
    lines.extend(["", "## Roadmap"])
    for step in payload.get("roadmap", []):
        lines.append(f"- {step.get('phase')} ({step.get('duration')})")
    return "\n".join(lines)
