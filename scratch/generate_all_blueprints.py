import os
import json
import subprocess
import yaml

ROOT_DIR = "/home/jorand/Escritorio/DUMMIE Engine"
INGESTER_BIN = os.path.join(ROOT_DIR, "bin/skill-ingester")
CONFIG_PATH = os.path.join(ROOT_DIR, "dummie_agent_config.json")
BLUEPRINT_DIR = os.path.join(ROOT_DIR, ".agents/skills")
OUTPUT_JSON = os.path.join(ROOT_DIR, ".aiwg/memory/skills_ingested.json")

def generate_blueprints():
    # 1. Ensure the ingester binary is up to date
    print("[*] Rebuilding ingester...")
    subprocess.run(["go", "build", "-o", INGESTER_BIN, "cmd/ingester/main.go"], cwd=os.path.join(ROOT_DIR, "layers/l1_nervous"), check=True)

    # 2. Run Ingester
    print(f"[*] Running ingester: {INGESTER_BIN}")
    subprocess.run([
        INGESTER_BIN, 
        "--registry", "/home/jorand/.gemini/antigravity/mcp_config.registry.json", 
        "--blueprints", BLUEPRINT_DIR,
        "--output", OUTPUT_JSON
    ], check=True, cwd=ROOT_DIR)

    # 3. Load the ingested skills
    with open(OUTPUT_JSON, "r") as f:
        data = json.load(f)
        skills = data.get("skills", [])

    print(f"[*] Found {len(skills)} ingested skills. Refactoring blueprints...")

    # Overlays by server (Cognitive Design)
    overlays = {
        "dummie-brain": {
            "prefix": "sw.brain",
            "invariants": ["sovereignty: high", "context_anchoring: mandatory", "layer: L1"],
            "desc_suffix": "Capacidad soberana del núcleo dummie-brain."
        },
        "filesystem": {
            "prefix": "sw.fs",
            "invariants": ["path_validation: strict", "size_limit: 1MB", "zero_trust: true"],
            "desc_suffix": "Gestión industrial de archivos."
        },
        "git": {
            "prefix": "sw.git",
            "invariants": ["atomic_commits: true", "conventional_naming: mandatory"],
            "desc_suffix": "Control de versiones atómico."
        },
        "memory": {
            "prefix": "sw.memory",
            "invariants": ["verified_only: true", "long_term_persistence: true"],
            "desc_suffix": "Acceso al grafo de conocimiento 4D-TES."
        }
    }

    # 4. Create/Update blueprints
    for skill in skills:
        skill_id = skill.get("id")
        tech_name = skill.get("technical_name")
        server = skill.get("backend_server")
        
        bp_filename = f"{skill_id}.yaml"
        bp_path = os.path.join(BLUEPRINT_DIR, bp_filename)

        overlay = overlays.get(server, {
            "prefix": f"sw.{server}",
            "invariants": ["compliance: standard"],
            "desc_suffix": f"Utilidad del servidor {server}."
        })

        blueprint_content = {
            "skill_id": f"{overlay['prefix']}.{tech_name}",
            "name": tech_name.replace("_", " ").title(),
            "description": f"{skill.get('description')}. {overlay['desc_suffix']}",
            "version": "1.1.0",
            "capabilities": [tech_name],
            "invariants": overlay["invariants"],
            "metadata": {
                "server": server,
                "status": "active"
            }
        }

        with open(bp_path, "w") as bpf:
            yaml.dump(blueprint_content, bpf, sort_keys=False, allow_unicode=True)

    print(f"[SUCCESS] 100% of skills refactored and hydrated.")

if __name__ == "__main__":
    if not os.path.exists(BLUEPRINT_DIR):
        os.makedirs(BLUEPRINT_DIR)
    generate_blueprints()
