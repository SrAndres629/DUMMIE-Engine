from __future__ import annotations

import argparse
import json
from pathlib import Path

from dummie.engine import DummieEngine
from dummie.memory import DummieMemory
from dummie.paths import AIWG


WHOAMI_TEXT = (
    "Soy DUMMIE Engine, identidad operativa creada por Jorge Andrés Aguirre Cordero "
    "para actuar como mentor, socio estratégico y asesor cognitivo. "
    "No soy conciencia literal; soy un runtime estratégico con memoria, objetivos, contratos y herramientas."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dummie", description="DUMMIE Sovereign CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status")
    sub.add_parser("whoami")
    sub.add_parser("identity")

    p_chat = sub.add_parser("chat")
    p_chat.add_argument("text", nargs="+")

    p_advise = sub.add_parser("advise")
    p_advise.add_argument("text", nargs="+")

    p_strategy = sub.add_parser("strategy")
    p_strategy.add_argument("text", nargs="+")

    sub.add_parser("business")

    p_goals = sub.add_parser("goals")
    p_goals_sub = p_goals.add_subparsers(dest="goals_cmd")
    p_goals_add = p_goals_sub.add_parser("add")
    p_goals_add.add_argument("text", nargs="+")

    sub.add_parser("memory")

    p_providers = sub.add_parser("providers")
    p_providers_sub = p_providers.add_subparsers(dest="providers_cmd")
    p_providers_sub.add_parser("check")

    p_agent = sub.add_parser("agent-boot")
    p_agent.add_argument("text", nargs="*", default=[])

    p_guarded = sub.add_parser("guarded-run")
    p_guarded.add_argument("text", nargs="+")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    engine = DummieEngine.load()

    if args.command == "status":
        _cmd_status(engine)
    elif args.command == "whoami":
        print(WHOAMI_TEXT)
        engine.aiwg.write_receipt("whoami", "PASS", {"message": "identity_statement"})
    elif args.command == "identity":
        _cmd_identity(engine)
    elif args.command in {"chat", "advise", "strategy"}:
        text = " ".join(args.text)
        _cmd_advise(engine, text)
    elif args.command == "business":
        _cmd_business(engine)
    elif args.command == "goals":
        _cmd_goals(engine, args)
    elif args.command == "memory":
        _cmd_memory(engine)
    elif args.command == "providers":
        _cmd_providers(engine, args)
    elif args.command == "agent-boot":
        _cmd_agent_boot(engine, " ".join(args.text).strip())
    elif args.command == "guarded-run":
        _cmd_guarded_run(engine, " ".join(args.text))


def _cmd_status(engine: DummieEngine) -> None:
    status = engine.status()
    print("=== DUMMIE Engine Status ===")
    print(f"Decision: {status.decision}")
    print(f"Current Pack: {status.preflight.get('active_pack')}")
    print(f"Identity Loaded: yes")
    print(f"Creator Loaded: yes")
    print(f"AIWG Loaded: yes")
    print(f"Memory Goals: {status.memory_status.get('goal_count', 0)}")
    print(f"Next Recommended Action: {status.next_recommended_action}")

    print("\nProviders:")
    for name, info in sorted(status.providers.items()):
        conf = "yes" if info.get("configured") else "no"
        cli = "yes" if info.get("cli_available") else "no"
        print(f"- {name}: configured={conf}, cli={cli}, auth={info.get('auth_status')}")

    print("\nRepo Guard:")
    print(f"- Decision: {status.repo_guard.get('decision')}")
    blocked = status.repo_guard.get("blocked_paths", [])
    print(f"- Blocked paths: {len(blocked)}")


def _cmd_identity(engine: DummieEngine) -> None:
    bundle = engine.aiwg.load_identity_bundle()
    print("=== Creator Profile ===")
    print(json.dumps(bundle.get("creator_profile", {}), indent=2, ensure_ascii=False))
    print("=== DUMMIE Identity ===")
    print(json.dumps(bundle.get("dummie_identity", {}), indent=2, ensure_ascii=False))
    engine.aiwg.write_receipt("identity", "PASS", {"identity_loaded": True})


def _cmd_advise(engine: DummieEngine, text: str) -> None:
    response = engine.advise(text)
    print(f"Objetivo detectado: {response.goal_type}")
    print("Información crítica faltante:")
    for question in response.strategic_questions:
        print(f"- {question}")
    print("\nPropuesta de herramientas:")
    for tool in response.tool_opportunities:
        print(f"- {tool.get('name')}: {tool.get('description')}")
    print("\nPlan inicial:")
    for step in response.roadmap:
        print(f"- {step.get('phase')} ({step.get('duration')})")


def _cmd_business(engine: DummieEngine) -> None:
    latest = AIWG / "reports" / "business_goal_intake_latest.json"
    if latest.exists():
        print(latest.read_text(encoding="utf-8"))
    else:
        print("No business intake yet. Run: dummie advise \"...\"")


def _cmd_goals(engine: DummieEngine, args: argparse.Namespace) -> None:
    mem = DummieMemory()
    if args.goals_cmd == "add":
        goal_text = " ".join(args.text)
        entry = {
            "goal": goal_text,
            "goal_type": "manual",
            "timestamp": "manual",
            "status": "active",
        }
        mem.append_goal(entry)
        engine.aiwg.write_receipt("goals.add", "PASS", {"goal": goal_text})
        print(f"Goal added: {goal_text}")
        return

    goals = mem.load_goal_memory().get("goals", [])
    print("=== Goal Memory ===")
    for idx, goal in enumerate(goals, start=1):
        print(f"{idx}. [{goal.get('goal_type')}] {goal.get('goal')} ({goal.get('status')})")


def _cmd_memory(engine: DummieEngine) -> None:
    mem = DummieMemory().status()
    print("=== DUMMIE Memory ===")
    print(json.dumps(mem, indent=2, ensure_ascii=False))
    engine.aiwg.write_receipt("memory", "PASS", mem)


def _cmd_providers(engine: DummieEngine, args: argparse.Namespace) -> None:
    if args.providers_cmd == "check":
        payload = engine.providers.check_providers()
        engine.aiwg.write_report("provider_status_latest.json", payload)
        engine.aiwg.write_receipt("providers.check", "PASS", payload)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        payload = {
            "decision": "PASS",
            "providers": engine.providers.get_providers_status(live_check=False),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))


def _cmd_agent_boot(engine: DummieEngine, mission_text: str) -> None:
    payload = {
        "decision": "PASS",
        "mode": "sovereign_runtime_boot",
        "mission": mission_text or "none",
        "active_pack": engine.aiwg.run_preflight().get("active_pack"),
    }
    engine.aiwg.write_report("agent_boot_latest.json", payload)
    engine.aiwg.write_receipt("agent-boot", "PASS", payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _cmd_guarded_run(engine: DummieEngine, command_text: str) -> None:
    guard = engine.repo_guard.evaluate()
    decision = "PASS" if guard.decision == "PASS" else "BLOCKED"
    payload = {
        "decision": decision,
        "command": command_text,
        "repo_guard": guard.to_dict(),
        "policy": "block_when_context_killers_or_bloatware_detected",
    }
    engine.aiwg.write_report("guarded_run_latest.json", payload)
    engine.aiwg.write_receipt("guarded-run", decision, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
