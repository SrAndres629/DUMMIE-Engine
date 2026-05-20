#!/usr/bin/env python3
"""
AIWG Guarded Run Entrypoint

This script acts as the required wrapper for any agentic execution.
It enforces the AIWG Native Operating Kernel flow:
1. aiwg_preflight
2. aiwg_context_loader
3. aiwg_context_capsule_builder
4. aiwg_token_budgeter
5. aiwg_mutation_router
6. Execution
7. aiwg_receipt_writer
8. aiwg_postflight
"""

import sys
import os
import argparse
from pathlib import Path

# Add layers to path
workspace_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(workspace_root))

from layers.l2_brain.aiwg_kernel.kernel import AIWGKernel

def main():
    parser = argparse.ArgumentParser(description="Guarded Agent Execution")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="The command to execute securely")
    args = parser.parse_args()

    # argparse.REMAINDER might leave an empty list or keep '--'
    cmd_args = args.command
    if cmd_args and cmd_args[0] == "--":
        cmd_args = cmd_args[1:]
    
    if not cmd_args:
        parser.print_help()
        sys.exit(1)

    kernel = AIWGKernel(workspace_root=workspace_root)
    
    command_str = " ".join(cmd_args)
    print(f"=== [GUARDED RUN] Requesting execution: {command_str} ===")

    # 1. Preflight
    pf = kernel.aiwg_preflight()
    if pf.get("status") != "PASS":
        print("[GUARDED RUN] ABORT: Preflight failed.")
        sys.exit(1)

    # 2. Mutation Router
    if not kernel.aiwg_mutation_router(command_str):
        print(f"[GUARDED RUN] ABORT: Mutation rejected for command '{command_str}'.")
        sys.exit(1)

    # 3. Context & Economy (Simulated usage before execution)
    payload = {"target_files": ["ANTIGRAVITY.md"]} # In a real scenario, infer from command
    context = kernel.aiwg_context_loader(payload)
    capsule = kernel.aiwg_context_capsule_builder(context)
    if not kernel.aiwg_token_budgeter(capsule):
        print("[GUARDED RUN] ABORT: Token budget exceeded.")
        sys.exit(1)

    # 4. Execution
    print(f"=== [GUARDED RUN] Executing: {command_str} ===")
    import time
    start_time = time.time()
    exit_code = os.system(command_str)
    duration = time.time() - start_time

    # 5. Receipt & Postflight
    receipt_id = kernel.aiwg_receipt_writer(command_str, exit_code, duration)
    kernel.aiwg_postflight(receipt_id)

    print(f"=== [GUARDED RUN] Completed. Receipt ID: {receipt_id} ===")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
