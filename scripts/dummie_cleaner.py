#!/usr/bin/env python3
import os
import shutil
import time

def clean_artifacts():
    print("=== [DUMMIE CLEANER] Purging build artifacts... ===")
    count_pyc = 0
    count_cache = 0
    
    for root, dirs, files in os.walk("."):
        # Skip hidden directories except .aiwg if needed (but usually safe to clean cache there too)
        if "/." in root and "/.aiwg" not in root:
            continue
            
        for file in files:
            if file.endswith(".pyc") or file.endswith(".pyo"):
                os.remove(os.path.join(root, file))
                count_pyc += 1
                
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))
                count_cache += 1
                
    print(f"Removed {count_pyc} .pyc files and {count_cache} __pycache__ directories.")

if __name__ == "__main__":
    start = time.time()
    clean_artifacts()
    print(f"Cleanup finished in {time.time() - start:.2f}s")
