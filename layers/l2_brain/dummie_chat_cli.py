from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Allow direct script execution
if __package__ in {None, ""}:
    _ROOT = Path(__file__).resolve().parents[2]
    if str(_ROOT) not in sys.path:
        sys.path.append(str(_ROOT))
    _L2 = _ROOT / "layers" / "l2_brain"
    if str(_L2) not in sys.path:
        sys.path.append(str(_L2))

from layers.l2_brain.repo_intelligence_query import query_repo_intelligence
from layers.l2_brain.context_enforcement_gate import run_context_enforcement_gate


@dataclass
class DummieChatResponse:
    decision: str = "PASS"
    answer: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    recommended_next_actions: list[str] = field(default_factory=list)
    context_strategy: str = ""
    warnings: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DummieChatCli:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"

    def handle_query(self, query_text: str) -> DummieChatResponse:
        query_text = query_text.strip().lower()
        
        # Determine intent
        intent = "unknown"
        if "status" in query_text: intent = "status"
        elif "next" in query_text or "do next" in query_text: intent = "next"
        elif "debt" in query_text: intent = "technical_debt"
        elif "capabilities" in query_text or "scorecard" in query_text: intent = "capabilities"
        elif "backlog" in query_text: intent = "integration_backlog"
        elif "find" in query_text: intent = "repo_query"
        elif "context" in query_text: intent = "context"
        elif "help" in query_text: intent = "help"

        # Context Gate Enforcement
        gate_request = {
            "request_id": f"chat_{self._utc_now()}",
            "user_intent": intent,
            "task_type": "analysis" if intent in ["status", "next", "technical_debt"] else "unknown",
            "requires_code_read": False
        }
        gate_decision = run_context_enforcement_gate(gate_request, aiwg_root=self.aiwg_root)
        
        if intent == "status":
            return self._cmd_status(gate_decision)
        elif intent == "next":
            return self._cmd_next(gate_decision)
        elif intent == "technical_debt":
            return self._cmd_debt(gate_decision)
        elif intent == "capabilities":
            return self._cmd_capabilities(gate_decision)
        elif intent == "integration_backlog":
            return self._cmd_backlog(gate_decision)
        elif intent == "repo_query":
            return self._cmd_query(query_text, gate_decision)
        elif intent == "help":
            return self._cmd_help()
        
        return DummieChatResponse(
            decision="PASS",
            answer=f"I understood your intent as '{intent}', but I don't have a specific handler for it yet.",
            context_strategy=gate_decision.decision,
            generated_at=self._utc_now()
        )

    def _cmd_status(self, gate: Any) -> DummieChatResponse:
        pos = self._load_json(self.aiwg_root / "evolution" / "current_position.json")
        phase = pos.get("current_phase", "unknown")
        name = pos.get("current_phase_name", "unknown")
        return DummieChatResponse(
            answer=f"System is currently in phase {phase} ({name}). Plan V1 runtime evolution is complete.",
            evidence_refs=[".aiwg/evolution/current_position.json"],
            context_strategy=gate.decision,
            generated_at=self._utc_now()
        )

    def _cmd_next(self, gate: Any) -> DummieChatResponse:
        seed = self._load_json(self.aiwg_root / "evolution" / "next_phase_seed.json")
        next_phase = seed.get("next_phase", "unknown")
        objective = seed.get("objective", "no_objective_defined")
        return DummieChatResponse(
            answer=f"The next required phase is {next_phase}. Objective: {objective}",
            evidence_refs=[".aiwg/evolution/next_phase_seed.json"],
            context_strategy=gate.decision,
            generated_at=self._utc_now()
        )

    def _cmd_debt(self, gate: Any) -> DummieChatResponse:
        debt = self._load_json(self.reports_root / "technical_debt_intelligence_latest.json")
        findings = debt.get("findings", [])
        summary = f"Found {len(findings)} technical debt items."
        if findings:
            summary += "\nTop items:"
            for f in findings[:3]:
                summary += f"\n- [{f['severity']}] {f['finding_id']}: {f['recommended_action']}"
        
        return DummieChatResponse(
            answer=summary,
            evidence_refs=[".aiwg/reports/technical_debt_intelligence_latest.json"],
            context_strategy=gate.decision,
            generated_at=self._utc_now()
        )

    def _cmd_capabilities(self, gate: Any) -> DummieChatResponse:
        scorecard = self._load_json(self.reports_root / "plan_v1_runtime_capability_scorecard.json")
        caps = scorecard.get("capabilities", [])
        return DummieChatResponse(
            answer=f"System has {len(caps)} scored capabilities. Most are operational/advisory.",
            evidence_refs=[".aiwg/reports/plan_v1_runtime_capability_scorecard.json"],
            context_strategy=gate.decision,
            generated_at=self._utc_now()
        )

    def _cmd_backlog(self, gate: Any) -> DummieChatResponse:
        backlog = self._load_json(self.reports_root / "integration_backlog.json")
        items = backlog.get("items", [])
        return DummieChatResponse(
            answer=f"Integration backlog contains {len(items)} items.",
            evidence_refs=[".aiwg/reports/integration_backlog.json"],
            context_strategy=gate.decision,
            generated_at=self._utc_now()
        )

    def _cmd_query(self, query_text: str, gate: Any) -> DummieChatResponse:
        # Naive extraction of query params
        q = {}
        if "runtime" in query_text: q["is_runtime"] = True
        if "test" in query_text: q["is_test"] = True
        if "untested" in query_text: q["no_tests"] = True
        if "python" in query_text: q["language"] = "python"
        
        res = query_repo_intelligence(q, aiwg_root=self.aiwg_root)
        answer = f"Found {res.count} files matching your query."
        if res.results:
            answer += "\nSamples:"
            for f in res.results[:5]:
                answer += f"\n- {f['path']} ({f['artifact_type']})"

        return DummieChatResponse(
            answer=answer,
            evidence_refs=[".aiwg/reports/repo_intelligence_query_latest.json"],
            context_strategy=gate.decision,
            generated_at=self._utc_now()
        )

    def _cmd_help(self) -> DummieChatResponse:
        help_text = """Available commands:
- status: Show current system phase.
- next: Show next phase and objective.
- technical debt: Show top debt findings.
- capabilities: Show capability scorecard summary.
- integration backlog: Show backlog items.
- find [runtime|test|untested|python]: Query the repository intelligence.
- help: Show this message."""
        return DummieChatResponse(answer=help_text, generated_at=self._utc_now())

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists(): return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main():
    chat = DummieChatCli()
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "status"
    response = chat.handle_query(query)
    
    # Save output
    reports_dir = Path(".aiwg/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "dummie_chat_cli_latest.json").write_text(
        json.dumps(response.to_dict(), indent=2) + "\n", encoding="utf-8"
    )
    
    print(json.dumps(response.to_dict(), indent=2))

if __name__ == "__main__":
    main()
