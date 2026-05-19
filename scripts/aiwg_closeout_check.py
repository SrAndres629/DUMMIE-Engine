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
    print("=== [AIWG CLOSEOUT CHECK] ===")
    
    # 1. Closeout
    run_cmd(["python3", "scripts/aiwg_pack_guard.py", "closeout"])
    
    print("SUCCESS: Closeout governance checks passed successfully!")
    sys.exit(0)

if __name__ == "__main__":
    main()
