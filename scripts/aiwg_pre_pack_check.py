#!/usr/bin/env python3
import sys
import subprocess

def run_cmd(args):
    print(f"Executing: {' '.join(args)}...")
    res = subprocess.run(args, capture_output=False)
    if res.returncode != 0:
        print(f"ERROR: Command failed with exit code {res.returncode}")
        sys.exit(res.returncode)

def main():
    print("=== [AIWG PRE-PACK CHECK] ===")
    
    # 1. Preflight
    run_cmd(["python3", "scripts/aiwg_pack_guard.py", "preflight"])
    
    # 2. Distance
    run_cmd(["python3", "scripts/aiwg_pack_guard.py", "distance"])
    
    # 3. Next Pack
    run_cmd(["python3", "scripts/aiwg_pack_guard.py", "next-pack"])
    
    print("SUCCESS: All pre-pack governance checks passed successfully!")
    sys.exit(0)

if __name__ == "__main__":
    main()
