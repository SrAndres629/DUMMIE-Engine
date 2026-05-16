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
from layers.l2_brain.memory_spine_entrypoint import retrieve_memory_for_intent
from layers.l2_brain.metacognitive_loop_runtime import run_metacognitive_loop
from layers.l2_brain.session_store import SessionStore



@dataclass
class DummieChatResponse:
    decision: str = "PASS"
    answer: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    recommended_next_actions: list[str] = field(default_factory=list)
    context_strategy: str = ""
    warnings: list[str] = field(default_factory=list)
    memory_spine: dict[str, Any] = field(default_factory=dict)
    memory_spine_used: bool = False
    mental_model: dict[str, Any] = field(default_factory=dict)
    cognitive_frame: dict[str, Any] = field(default_factory=dict)
    metacognitive_loop: dict[str, Any] = field(default_factory=dict)
    quality_gate: dict[str, Any] = field(default_factory=dict)
    epistemic_state: dict[str, Any] = field(default_factory=dict)
    bias_report: dict[str, Any] = field(default_factory=dict)
    dialectic: dict[str, Any] = field(default_factory=dict)
    evolution_delta: dict[str, Any] = field(default_factory=dict)
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
        if "status" in query_text:
            intent = "status"
        elif "next" in query_text or "do next" in query_text:
            intent = "next"
        elif "debt" in query_text:
            intent = "technical_debt"
        elif "capabilities" in query_text or "scorecard" in query_text:
            intent = "capabilities"
        elif "backlog" in query_text:
            intent = "integration_backlog"
        elif "find" in query_text and "untested" in query_text:
            intent = "repo_query"
        elif "context for" in query_text:
            intent = "context"
        elif "repo intelligence" in query_text or "find" in query_text:
            intent = "repo_query"
        elif "benchmark" in query_text or "token" in query_text:
            intent = "token_benchmark"
        elif "ready" in query_text or "calibration" in query_text:
            intent = "readiness_calibration"
        elif "memory" in query_text or "spine" in query_text:
            intent = "memory_spine"
        elif "audit" in query_text or "entrypoint" in query_text or "enforcement" in query_text:
            intent = "entrypoint_audit"
        elif "help" in query_text:
            intent = "help"

        # Context Gate Enforcement
        gate_request = {
            "request_id": f"chat_{self._utc_now()}",
            "user_intent": intent,
            "task_type": "analysis" if intent in ["status", "next", "technical_debt", "readiness_calibration", "entrypoint_audit"] else "unknown",
            "requires_code_read": False
        }
        gate_decision = run_context_enforcement_gate(gate_request, aiwg_root=self.aiwg_root)

        # Memory Spine Retrieval (BEFORE response generation)
        memory_result = retrieve_memory_for_intent(intent, aiwg_root=self.aiwg_root)

        response: DummieChatResponse | None = None
        if intent == "status":
            response = self._cmd_status(gate_decision)
        elif intent == "next":
            response = self._cmd_next(gate_decision)
        elif intent == "technical_debt":
            response = self._cmd_debt(gate_decision)
        elif intent == "capabilities":
            response = self._cmd_capabilities(gate_decision)
        elif intent == "integration_backlog":
            response = self._cmd_backlog(gate_decision)
        elif intent == "repo_query":
            response = self._cmd_query(query_text, gate_decision)
        elif intent == "token_benchmark":
            response = self._cmd_token_benchmark(gate_decision)
        elif intent == "readiness_calibration":
            response = self._cmd_readiness_calibration(gate_decision)
        elif intent == "memory_spine":
            response = self._cmd_memory_spine(gate_decision, memory_result)
        elif intent == "entrypoint_audit":
            response = self._cmd_entrypoint_audit(gate_decision)
        elif intent == "help":
            response = self._cmd_help()
        else:
            response = DummieChatResponse(
                decision="PASS",
                answer=f"I understood your intent as '{intent}', but I don't have a specific handler for it yet.",
                context_strategy=gate_decision.decision,
                generated_at=self._utc_now()
            )

        # Attach memory metadata to every response
        response.memory_spine = memory_result.to_dict()
        response.memory_spine_used = True
        if memory_result.status == "DEGRADED_WITH_FILE_BACKED_MEMORY":
            response.warnings.append("Memory spine is DEGRADED. Using file-backed fallback.")

        # Phase Pack 5: Metacognitive Loop
        try:
            m_loop = run_metacognitive_loop(query_text, aiwg_root=self.aiwg_root)
            response.metacognitive_loop = m_loop
            response.quality_gate = m_loop.get("quality_gate", {})
            response.epistemic_state = m_loop.get("epistemic_state", {})
            response.bias_report = m_loop.get("bias_report", {})
            response.dialectic = m_loop.get("dialectical_review", {})
            response.evolution_delta = m_loop.get("evolution_delta", {})
            
            reports_root = self.aiwg_root / "reports"
            if (reports_root / "mental_model_runtime_latest.json").exists():
                response.mental_model = json.loads((reports_root / "mental_model_runtime_latest.json").read_text())
            if (reports_root / "cognitive_frame_latest.json").exists():
                response.cognitive_frame = json.loads((reports_root / "cognitive_frame_latest.json").read_text())
        except Exception as e:
            response.warnings.append(f"metacognition_degraded: {e}")



        # Record Learning Episode (Cognitive Loop) - Operationalization Pack 4
        try:


            # aiwg_root is .aiwg, SessionStore needs repo_root
            store = SessionStore(self.aiwg_root.resolve().parent)
            
            # Ensure CURRENT session exists
            try:
                store.load_session("CURRENT")
            except FileNotFoundError:
                store.create_session("CURRENT", {"description": "Auto-generated daily cockpit session"})

            episode = {
                "query": query_text,
                "intent": intent,
                "answer": response.answer,
                "timestamp": self._utc_now(),
                "evidence_refs": response.evidence_refs,
                "decision": response.decision
            }
            store.append_learning_episode("CURRENT", episode)
        except Exception as e:
            response.warnings.append(f"Learning loop warning: could not record episode in CURRENT session ({e})")

        return response


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

    def _cmd_token_benchmark(self, gate: Any) -> DummieChatResponse:
        bench = self._load_json(self.reports_root / "token_economy_benchmark_latest.json")
        if not bench:
            # Run benchmark inline
            try:
                from layers.l2_brain.token_economy_benchmark import run_token_economy_benchmark
                result = run_token_economy_benchmark()
                bench = result.to_dict()
            except Exception as exc:
                return DummieChatResponse(
                    answer=f"Token benchmark not available: {exc}",
                    warnings=[str(exc)],
                    context_strategy=gate.decision,
                    generated_at=self._utc_now()
                )
        ratio = bench.get("raw_to_dossier_reduction_ratio", 0)
        score = bench.get("token_efficiency_score", 0)
        return DummieChatResponse(
            answer=f"Token Economy Benchmark: {ratio}x reduction ratio, Efficiency Score: {score}/100. Measurement: deterministic_estimate.",
            evidence_refs=[".aiwg/reports/token_economy_benchmark_latest.json"],
            context_strategy=gate.decision,
            generated_at=self._utc_now()
        )

    def _cmd_readiness_calibration(self, gate: Any) -> DummieChatResponse:
        cal = self._load_json(self.reports_root / "readiness_score_calibration_latest.json")
        if not cal:
            try:
                from layers.l2_brain.readiness_score_calibrator import run_readiness_score_calibration
                result = run_readiness_score_calibration()
                cal = result.to_dict()
            except Exception as exc:
                return DummieChatResponse(
                    answer=f"Readiness calibration not available: {exc}",
                    warnings=[str(exc)],
                    context_strategy=gate.decision,
                    generated_at=self._utc_now()
                )
        scores = cal.get("calibrated_scores", {})
        findings = cal.get("findings", [])
        summary = "Calibrated Readiness Scores:\n" + "\n".join([f"- {k}: {v}" for k, v in scores.items()])
        if findings:
            summary += f"\n\nFindings ({len(findings)}):"
            for f in findings:
                summary += f"\n- [{f['severity']}] {f['id']}: {f['description']}"
        return DummieChatResponse(
            answer=summary,
            evidence_refs=[".aiwg/reports/readiness_score_calibration_latest.json"],
            context_strategy=gate.decision,
            generated_at=self._utc_now()
        )

    def _cmd_memory_spine(self, gate: Any, memory: Any) -> DummieChatResponse:
        return DummieChatResponse(
            answer=f"Memory Spine Status: {memory.status}. Graph: {memory.graph_status}. Found {len(memory.learning_episode_refs)} episode refs, {len(memory.vault_refs)} vault refs.",
            evidence_refs=[".aiwg/reports/memory_spine_entrypoint_latest.json"],
            context_strategy=gate.decision,
            generated_at=self._utc_now()
        )

    def _cmd_entrypoint_audit(self, gate: Any) -> DummieChatResponse:
        audit = self._load_json(self.reports_root / "entrypoint_enforcement_audit_latest.json")
        if not audit:
            try:
                from layers.l2_brain.entrypoint_enforcement_auditor import run_entrypoint_enforcement_audit
                audit = run_entrypoint_enforcement_audit()
            except Exception as exc:
                return DummieChatResponse(
                    answer=f"Entrypoint audit not available: {exc}",
                    warnings=[str(exc)],
                    context_strategy=gate.decision,
                    generated_at=self._utc_now()
                )
        audits = audit.get("audits", [])
        no_spine = [a for a in audits if not a.get("uses_memory_spine")]
        no_gate = [a for a in audits if a.get("bypasses_context_gate")]
        summary = f"Entrypoint Audit: {len(audits)} entrypoints checked.\n"
        summary += f"- {len(no_spine)} missing memory spine integration\n"
        summary += f"- {len(no_gate)} bypass context gate"
        return DummieChatResponse(
            answer=summary,
            evidence_refs=[".aiwg/reports/entrypoint_enforcement_audit_latest.json"],
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
        q: dict[str, Any] = {}
        if "runtime" in query_text:
            q["is_runtime"] = True
        if "test" in query_text:
            q["is_test"] = True
        if "untested" in query_text:
            q["no_tests"] = True
        if "python" in query_text:
            q["language"] = "python"

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
- repo intelligence / find [runtime|test|untested]: Query the repository intelligence.
- find untested runtime: Find runtimes without tests.
- context for <path>: Get context for a path.
- show memory spine: Show memory spine status.
- benchmark token economy: Run token economy benchmark.
- show readiness calibration / am I really ready?: Show readiness calibration.
- show entrypoint enforcement: Show entrypoint enforcement audit.
- help: Show this message."""
        return DummieChatResponse(answer=help_text, generated_at=self._utc_now())

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
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
