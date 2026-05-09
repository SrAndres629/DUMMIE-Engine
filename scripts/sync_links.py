import os
import re
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(PROJECT_ROOT, "doc")

def sync_links():
    # 1. Build an index of all relevant files in doc/
    file_index = {}
    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(('.md', '.feature', '.json')):
                # Store relative path from doc/ to the file
                rel_path_from_doc = os.path.relpath(os.path.join(root, file), DOCS_DIR)
                file_index[file] = rel_path_from_doc

    print(f"Indexed {len(file_index)} files in doc/")

    # 2. Iterate and update links
    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(('.md', '.feature')):
                file_path = os.path.join(root, file)
                changed = False
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Regex to find [text](path)
                # We are looking for paths that are just filenames or old relative paths
                def replace_link(match):
                    text = match.group(1)
                    old_path = match.group(2)
                    
                    # Ignore external links
                    if old_path.startswith(('http', 'mailto', '#')):
                        return match.group(0)
                        
                    basename = os.path.basename(old_path)
                    
                    if basename in file_index:
                        target_abs_path = os.path.join(DOCS_DIR, file_index[basename])
                        new_rel_path = os.path.relpath(target_abs_path, os.path.dirname(file_path))
                        
                        if new_rel_path != old_path:
                            nonlocal changed
                            changed = True
                            return f"[{text}]({new_rel_path})"
                    
                    return match.group(0)

                new_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)

                if changed:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"[✓] Updated links in: {os.path.relpath(file_path, PROJECT_ROOT)}")

if __name__ == "__main__":
    sync_links()
