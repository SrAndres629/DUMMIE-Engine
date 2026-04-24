#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path

# Raíz del proyecto DUMMIE Engine
ROOT_DIR = Path(__file__).parent.parent.absolute()
AIWG_DIR = ROOT_DIR / ".aiwg"
DOC_DIR = ROOT_DIR / "doc"

def get_tree(depth=2):
    """Genera el árbol de directorios en tiempo real."""
    tree_str = []
    for root, dirs, files in os.walk(ROOT_DIR):
        # Ignorar carpetas ocultas o muy pesadas
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'deps', '_build']]
        level = str(root).replace(str(ROOT_DIR), '').count(os.sep)
        if level > depth:
            continue
        indent = ' ' * 4 * level
        tree_str.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if not f.startswith('.'):
                tree_str.append(f"{subindent}{f}")
    return "\n".join(tree_str)

def get_architecture():
    """Lee las reglas arquitectónicas más recientes (GEMINI.md)."""
    gemini_md = ROOT_DIR / "GEMINI.md"
    if gemini_md.exists():
        return gemini_md.read_text()
    return "Arquitectura no encontrada."

def get_active_specs():
    """Devuelve un resumen de las especificaciones SDD activas."""
    specs = []
    specs_dir = DOC_DIR / "specs"
    if specs_dir.exists():
        for file in specs_dir.rglob("*.md"):
            specs.append(f"- {file.relative_to(ROOT_DIR)}")
    return "\n".join(specs) if specs else "No hay specs activas."

def get_memory_state():
    """Consulta el estado del grafo 4D-TES."""
    # Aquí podríamos conectar a KùzuDB, por ahora leemos los ledgers físicos
    ledger = AIWG_DIR / "ledger" / "sovereign_resolutions.jsonl"
    if ledger.exists():
        with open(ledger, 'r') as f:
            lines = f.readlines()
            return f"Total resoluciones en memoria: {len(lines)}\nÚltima resolución:\n{lines[-1].strip()}"
    return "Memoria 4D-TES inactiva o vacía."

def get_metacognitive_header(agent_name="clean-coder-pro", source="PAH (Human)"):
    """Genera el bloque de consciencia para el agente."""
    header = {
        "identity": {
            "role": agent_name,
            "capabilities": ["SSH-Access", "4D-TES-Writing", "6D-Navigation"],
            "constraints": ["Token-Efficiency-Mandate", "Logic-Zero-Policy"]
        },
        "authority_source": source,
        "session": {
            "id": "SESSION-" + os.uname().nodename,
            "type": "Metacognitive-Mixed-State",
            "bridge": "Local-SSH-Tunnel"
        },
        "mission_rationale": "Optimizar el costo operativo mientras se mantiene la integridad soberana del código."
    }
    return json.dumps(header, indent=2)

def main():
    parser = argparse.ArgumentParser(description="DUMMIE Engine Context Oracle (SSH Endpoint)")
    parser.add_argument("--tree", action="store_true", help="Devuelve el árbol de archivos actual.")
    parser.add_argument("--arch", action="store_true", help="Devuelve las reglas de arquitectura SDD.")
    parser.add_argument("--specs", action="store_true", help="Lista las especificaciones activas.")
    parser.add_argument("--memory", action="store_true", help="Devuelve el estado de la memoria 4D.")
    parser.add_argument("--whoami", action="store_true", help="Genera el Header Metacognitivo de identidad.")
    
    args = parser.parse_args()
    
    if args.tree:
        print("=== ÁRBOL DE DIRECTORIOS EN TIEMPO REAL ===")
        print(get_tree())
    elif args.arch:
        print("=== REGLAS DE ARQUITECTURA (MAD 2026) ===")
        print(get_architecture())
    elif args.specs:
        print("=== ESPECIFICACIONES ACTIVAS ===")
        print(get_active_specs())
    elif args.memory:
        print("=== ESTADO DE MEMORIA 4D-TES ===")
        print(get_memory_state())
    elif args.whoami:
        print("=== METACOGNITIVE IDENTITY HEADER ===")
        print(get_metacognitive_header())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
