#!/usr/bin/env python3
import sys
from pathlib import Path

def generate_loci_diagram():
    repo_root = Path(__file__).resolve().parents[1]
    map_file = repo_root / "doc" / "PHYSICAL_MAP.md"
    
    if not map_file.exists():
        print("Error: doc/PHYSICAL_MAP.md not found.")
        return

    content = map_file.read_text(encoding="utf-8")
    
    mermaid = ["graph TD", "    subgraph Palacio_de_Loci"]
    
    current_layer = None
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("### L"):
            # Extract layer info
            layer_id = line.split(" ")[1]
            layer_name = line.split("(")[1].split(")")[0] if "(" in line else layer_id
            current_layer = layer_id
            mermaid.append(f'        {layer_id}["{layer_id}: {layer_name}"]')
        elif line.startswith("- **") and current_layer:
            # Extract components
            comp = line.split("**")[1]
            comp_id = comp.replace(" ", "_").lower()
            mermaid.append(f"        {current_layer} --> {current_layer}_{comp_id}[{comp}]")

    mermaid.append("    end")
    
    # Layer connections (Fixed architectural flow)
    mermaid.append("    L0 -- orquestación --> L2")
    mermaid.append("    L2 -- intención --> L3")
    mermaid.append("    L2 -- datos --> L1")
    mermaid.append("    L2 -- ejecución --> L5")
    mermaid.append("    L5 -- feedback --> L2")
    mermaid.append("    L1 -- memoria --> L2")
    
    print("\n".join(mermaid))

if __name__ == "__main__":
    generate_loci_diagram()
