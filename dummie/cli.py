from __future__ import annotations

# Spec: 203_agent_mesh_runtime

import argparse
import json
import sys

from dummie.engine import DummieEngine
from dummie.agent_mesh import AgentMeshRuntime
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
    p_chat.add_argument("text", nargs="*")
    p_chat.add_argument("-i", "--interactive", action="store_true")
    p_chat.add_argument("--low-cost", action="store_true")

    p_advise = sub.add_parser("advise")
    p_advise.add_argument("text", nargs="+")
    p_advise.add_argument("--low-cost", action="store_true")

    p_strategy = sub.add_parser("strategy")
    p_strategy.add_argument("text", nargs="+")
    p_strategy.add_argument("--low-cost", action="store_true")

    sub.add_parser("business")

    p_goals = sub.add_parser("goals")
    p_goals_sub = p_goals.add_subparsers(dest="goals_cmd")
    p_goals_add = p_goals_sub.add_parser("add")
    p_goals_add.add_argument("text", nargs="+")

    sub.add_parser("memory")
    sub.add_parser("loci")

    p_providers = sub.add_parser("providers")
    p_providers_sub = p_providers.add_subparsers(dest="providers_cmd")
    p_providers_sub.add_parser("check")

    p_agent = sub.add_parser("agent-boot")
    p_agent.add_argument("text", nargs="*", default=[])

    p_mesh = sub.add_parser("agent-mesh")
    p_mesh_sub = p_mesh.add_subparsers(dest="agent_mesh_cmd")
    p_mesh_sub.add_parser("bootstrap")
    p_mesh_sub.add_parser("status")
    p_mesh_send = p_mesh_sub.add_parser("send")
    p_mesh_send.add_argument("sender")
    p_mesh_send.add_argument("recipient")
    p_mesh_send.add_argument("topic")
    p_mesh_send.add_argument("body", nargs="+")
    p_mesh_read = p_mesh_sub.add_parser("read")
    p_mesh_read.add_argument("agent_id")
    p_mesh_read.add_argument("channel", choices=["inbox", "control", "outbox", "handoff"])

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
    elif args.command == "chat":
        text = " ".join(args.text).strip()
        if args.interactive:
            _cmd_chat_interactive(engine, low_cost=args.low_cost, seed_text=text)
        else:
            if not text:
                raise SystemExit("chat requires text or --interactive")
            _cmd_chat(engine, text, low_cost=args.low_cost)
    elif args.command in {"advise", "strategy"}:
        text = " ".join(args.text)
        _cmd_advise(engine, text, low_cost=args.low_cost)
    elif args.command == "business":
        _cmd_business(engine)
    elif args.command == "goals":
        _cmd_goals(engine, args)
    elif args.command == "memory":
        _cmd_memory(engine)
    elif args.command == "loci":
        _cmd_loci(engine)
    elif args.command == "providers":
        _cmd_providers(engine, args)
    elif args.command == "agent-boot":
        _cmd_agent_boot(engine, " ".join(args.text).strip())
    elif args.command == "agent-mesh":
        _cmd_agent_mesh(args)
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


def _cmd_agent_mesh(args: argparse.Namespace) -> None:
    runtime = AgentMeshRuntime()
    if args.agent_mesh_cmd == "bootstrap":
        print(json.dumps(runtime.bootstrap_mesh(), indent=2, ensure_ascii=False))
    elif args.agent_mesh_cmd == "status":
        print(json.dumps(runtime.status(), indent=2, ensure_ascii=False))
    elif args.agent_mesh_cmd == "send":
        print(
            json.dumps(
                runtime.send_message(
                    sender=args.sender,
                    recipient=args.recipient,
                    topic=args.topic,
                    body=" ".join(args.body),
                ),
                indent=2,
                ensure_ascii=False,
            )
        )
    elif args.agent_mesh_cmd == "read":
        print(json.dumps(runtime.read_channel(args.agent_id, args.channel), indent=2, ensure_ascii=False))
    else:
        raise SystemExit("agent-mesh requires: bootstrap, status, send, or read")


def _cmd_identity(engine: DummieEngine) -> None:
    bundle = engine.aiwg.load_identity_bundle()
    print("=== Creator Profile ===")
    print(json.dumps(bundle.get("creator_profile", {}), indent=2, ensure_ascii=False))
    print("=== DUMMIE Identity ===")
    print(json.dumps(bundle.get("dummie_identity", {}), indent=2, ensure_ascii=False))
    engine.aiwg.write_receipt("identity", "PASS", {"identity_loaded": True})


def _cmd_advise(engine: DummieEngine, text: str, low_cost: bool = False) -> None:
    if low_cost:
        _apply_low_cost_profile(engine, source_command="advise")
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


def _cmd_chat_interactive(engine: DummieEngine, low_cost: bool = False, seed_text: str = "") -> None:
    if low_cost:
        _apply_low_cost_profile(engine, source_command="chat.interactive")

    print("DUMMIE Chat interactive")
    print("Comandos: /help /status /providers /goals /memory /exit")
    if low_cost:
        print("Modo: LOW_COST (local/free-first, contexto mínimo)")

    if seed_text:
        _chat_turn(engine, seed_text, low_cost=low_cost)

    while True:
        try:
            user_text = input("jorge> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo de DUMMIE chat.")
            break

        if not user_text:
            continue
        if user_text.startswith("/"):
            if _handle_chat_command(engine, user_text):
                break
            continue

        _chat_turn(engine, user_text, low_cost=low_cost)


def _handle_chat_command(engine: DummieEngine, raw_cmd: str) -> bool:
    cmd = raw_cmd.strip().lower()
    if cmd in {"/exit", "/quit"}:
        print("Sesion finalizada.")
        return True
    if cmd == "/help":
        print("Comandos: /help /status /providers /goals /memory /exit")
        return False
    if cmd == "/status":
        _cmd_status(engine)
        return False
    if cmd == "/providers":
        _cmd_providers(engine, argparse.Namespace(providers_cmd="check"))
        return False
    if cmd == "/goals":
        _cmd_goals(engine, argparse.Namespace(goals_cmd=None, text=[]))
        return False
    if cmd == "/memory":
        _cmd_memory(engine)
        return False

    print(f"Comando no reconocido: {raw_cmd}")
    return False


def _chat_turn(engine: DummieEngine, user_text: str, low_cost: bool = False) -> None:
    response = engine.chat(user_text, low_cost=low_cost)
    print(
        "dummie> Pipeline: "
        f"pre={response.preprocessing_provider} "
        f"tier={response.routing_tier} "
        f"model={response.routing_model_id} "
        f"provider={response.selected_provider}"
    )
    print(f"dummie> Objetivo detectado: {response.goal_type}")
    if response.strategic_questions:
        print(f"dummie> Pregunta clave: {response.strategic_questions[0]}")
    if response.tool_opportunities:
        top_tool = response.tool_opportunities[0]
        print(f"dummie> Herramienta sugerida: {top_tool.get('name')}")
    if response.roadmap:
        first_step = response.roadmap[0]
        print(f"dummie> Siguiente paso: {first_step.get('phase')} ({first_step.get('duration')})")


def _cmd_chat(engine: DummieEngine, text: str, low_cost: bool = False) -> None:
    response = engine.chat(text, low_cost=low_cost)
    print("=== DUMMIE Runtime Chat ===")
    print(
        f"Pipeline: pre={response.preprocessing_provider} "
        f"tier={response.routing_tier} "
        f"model={response.routing_model_id} "
        f"provider={response.selected_provider}"
    )
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


def _apply_low_cost_profile(engine: DummieEngine, source_command: str) -> None:
    payload = {
        "decision": "PASS",
        "profile": "LOW_COST",
        "source_command": source_command,
        "policies": [
            "free_or_local_first",
            "minimize_context_expansion",
            "avoid_cloud_provider_by_default",
            "write_token_receipts",
        ],
        "notes": "This profile prioritizes zero-cost deterministic runtime and compact context handling.",
    }
    engine.aiwg.write_report("chat_low_cost_profile_latest.json", payload)
    engine.aiwg.write_receipt("low-cost-profile", "PASS", payload)


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


def _cmd_loci(engine: DummieEngine) -> None:
    print("=== DUMMIE Palacio de Loci (Mapa Físico) ===")
    try:
        import subprocess
        from dummie.paths import ROOT
        res = subprocess.run([sys.executable, str(ROOT / "scripts" / "dummie_loci.py")], capture_output=True, text=True)
        print(res.stdout)
        engine.aiwg.write_receipt("loci", "PASS", {"diagram": "mermaid"})
    except Exception as e:
        print(f"Error generando mapa: {e}")


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
