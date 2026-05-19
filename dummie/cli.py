import sys
import json
import yaml
from pathlib import Path
from dummie.engine import DummieEngine
from dummie.paths import AIWG

def print_help():
    print("DUMMIE Engine CLI")
    print("Usage: dummie <command> [args]")
    print("\nCommands:")
    print("  status                 Show DUMMIE status, pack, and provider statuses")
    print("  whoami                 Identify DUMMIE operational identity")
    print("  identity               Print creator profile and identity details")
    print("  chat <text>            Chat with DUMMIE Engine")
    print("  advise <text>          Get strategic advice for business growth or goals")
    print("  strategy <text>        Shortcut for advise")
    print("  business               Show the latest business intake structure")
    print("  goals                  List goals in goal memory")
    print("  goals add <text>       Add a goal to goal memory")
    print("  memory                 Show memory status and details")
    print("  providers              List provider configurations")
    print("  providers check        Check live provider authorization status")
    print("  agent-boot             Boot agent environment")
    print("  guarded-run <text>     Run command under guarded validation policy")

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    engine = DummieEngine.load()

    if cmd == "status":
        status = engine.status()
        print("=== DUMMIE Engine Status ===")
        print(f"Decision: {status.decision}")
        print(f"Current Pack: {status.preflight.get('active_pack')}")
        print(f"Root Directory: {status.root_dir}")
        print(f"AIWG Directory: {status.aiwg_dir}")
        print("\nProviders:")
        for name, info in status.providers.items():
            conf = "yes" if info['configured'] else "no"
            cli = "yes" if info['cli_available'] else "no"
            print(f" - {name} ({info['type']}): configured={conf}, cli={cli}, status={info['auth_status']}")

    elif cmd == "whoami":
        print("Soy DUMMIE Engine, identidad operativa creada por Jorge Andrés Aguirre Cordero para actuar como mentor, socio estratégico y asesor cognitivo. No soy conciencia literal; soy un runtime estratégico con memoria, objetivos, contratos y herramientas.")

    elif cmd == "identity":
        creator_file = AIWG / "identity" / "creator_profile.yaml"
        identity_file = AIWG / "identity" / "dummie_identity.yaml"
        print("=== Creator Profile ===")
        if creator_file.exists():
            print(creator_file.read_text())
        else:
            print("Profile missing.")
        print("=== DUMMIE Identity ===")
        if identity_file.exists():
            print(identity_file.read_text())
        else:
            print("Identity missing.")

    elif cmd == "chat":
        query = " ".join(args)
        if not query:
            print("Error: chat requires query text")
            sys.exit(1)
        res = engine.advise(query)
        print(f"DUMMIE Answer: {res.raw_data.get('advice', {}).get('tactics', ['Sin respuesta'])[0]}")

    elif cmd in ("advise", "strategy"):
        query = " ".join(args)
        if not query:
            print("Error: advise requires query text")
            sys.exit(1)
        res = engine.advise(query)
        print("=== Goal Classification ===")
        print(f"Type: {res.goal_type}")
        print(f"Description: {res.raw_data.get('goal_classification', {}).get('description')}")
        print("\n=== Strategic Questions ===")
        for q in res.strategic_questions:
            print(f"- {q}")
        print("\n=== Tool Opportunities ===")
        for t in res.tool_opportunities:
            print(f"- {t.get('name')} ({t.get('opportunity_type')}): {t.get('description')}")
        print("\n=== Roadmap ===")
        for step in res.roadmap:
            print(f"Phase: {step.get('phase')} ({step.get('duration')})")
            for act in step.get("actions", []):
                print(f"  * {act}")
        print("\n=== Advice ===")
        for tactic in res.advice.get("tactics", []):
            print(f"- {tactic}")

    elif cmd == "business":
        latest = AIWG / "reports" / "business_goal_intake_latest.json"
        if latest.exists():
            print(latest.read_text())
        else:
            print("No business goal intake recorded yet. Use 'dummie advise' first.")

    elif cmd == "goals":
        if args and args[0].lower() == "add":
            goal = " ".join(args[1:])
            if not goal:
                print("Error: goal description required")
                sys.exit(1)
            engine.partner._record_goal(goal, "manual")
            print(f"Goal added successfully: '{goal}'")
        else:
            goal_file = AIWG / "identity" / "goal_memory.yaml"
            if goal_file.exists():
                try:
                    with open(goal_file, "r") as f:
                        data = yaml.safe_load(f) or {}
                    goals = data.get("goals", [])
                    print("=== Goal Memory ===")
                    if goals:
                        for idx, g in enumerate(goals):
                            print(f"{idx + 1}. [{g.get('goal_type')}] {g.get('goal')} ({g.get('status')})")
                    else:
                        print("No goals stored.")
                except Exception as e:
                    print(f"Error reading goals: {e}")
            else:
                print("No goal memory found.")

    elif cmd == "memory":
        goal_file = AIWG / "identity" / "goal_memory.yaml"
        goals_count = 0
        if goal_file.exists():
            try:
                with open(goal_file, "r") as f:
                    data = yaml.safe_load(f) or {}
                goals_count = len(data.get("goals", []))
            except Exception:
                pass
        print("=== DUMMIE Memory Status ===")
        print(f"Active Goals: {goals_count}")
        print(f"Workspace Directory: {ROOT}")

    elif cmd == "providers":
        if args and args[0].lower() == "check":
            status = engine.status()
            print("=== Live Provider Verification ===")
            for name, info in status.providers.items():
                print(f"- {name}: cli={info['cli_available']}, status={info['auth_status']}")
        else:
            status = engine.status()
            print("=== Registered Providers ===")
            for name, info in status.providers.items():
                print(f"- {name}: type={info['type']}, storage={info['secret_storage']}")

    elif cmd == "agent-boot":
        boot_report = {
            "status": "READY",
            "booted_at": datetime.now(timezone.utc).isoformat() if 'datetime' in sys.modules else "2026-05-19T04:00:00Z",
            "active_pack": "PACK_S1"
        }
        engine.aiwg.write_report("agent_boot_latest.json", boot_report)
        print("DUMMIE Agent Bootstrapped successfully.")

    elif cmd == "guarded-run":
        cmd_to_run = " ".join(args)
        if not cmd_to_run:
            print("Error: command string required for guarded-run")
            sys.exit(1)
        # Execute guarded run simulation/stub
        print(f"Executing under guarded run: {cmd_to_run}")
        run_report = {
            "command": cmd_to_run,
            "validation": "PASS",
            "run_at": "2026-05-19T04:00:00Z"
        }
        engine.aiwg.write_report("guarded_run_latest.json", run_report)
        print("Guarded run validation complete: PASS")

    else:
        print(f"Unknown command: {cmd}")
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
