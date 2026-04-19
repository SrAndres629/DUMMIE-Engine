import os
import json
import re

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "doc")
PERSONALITY_REF = "DE-V2-ADR-004"

def update_personality_link(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Detectar capa
    layer_match = re.search(r'layer:\s*"(L0|L2|L3)"', content)
    if not layer_match:
        return False

    # Buscar bloque JSON
    json_match = re.search(r'(```json\s*\n)(.*?)(\n```)', content, re.DOTALL)
    if not json_match:
        return False

    prefix, json_str, suffix = json_match.groups()
    try:
        model = json.loads(json_str)
        if "personality_ref" not in model and "personality_filter" not in model:
            model["personality_ref"] = PERSONALITY_REF
            new_json = json.dumps(model, indent=2, ensure_ascii=False)
            new_content = content[:json_match.start(2)] + new_json + content[json_match.end(2):]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"Error in {file_path}: {e}")
    
    return False

if __name__ == "__main__":
    count = 0
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                if update_personality_link(os.path.join(root, file)):
                    count += 1
    print(f"Updated {count} files with Personality Link.")
