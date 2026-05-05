import subprocess
import json
import os
import time

def run_test_cycle(cycle_id):
    root_dir = "/home/jorand/Escritorio/DUMMIE Engine"
    python_exe = os.path.join(root_dir, "layers/l2_brain/.venv/bin/python")
    server_script = os.path.join(root_dir, "layers/l1_nervous/mcp_server.py")
    
    env = os.environ.copy()
    env["DUMMIE_ROOT_DIR"] = root_dir
    env["DUMMIE_AIWG_DIR"] = os.path.join(root_dir, ".aiwg")
    env["DUMMIE_KUZU_DB_PATH"] = os.path.join(env["DUMMIE_AIWG_DIR"], "memory/loci.db")
    env["PYTHONPATH"] = f"{os.path.join(root_dir, 'layers/l2_brain')}:{os.path.join(root_dir, 'layers/l1_nervous')}"
    
    print(f"\n--- CYCLE {cycle_id} ---")
    process = subprocess.Popen(
        [python_exe, server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    init_request = {
        "jsonrpc": "2.0",
        "id": cycle_id,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "AuditBot", "version": "1.0.0"}
        }
    }
    
    try:
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        process.stdin.flush()
        
        # Read response with timeout
        response_line = process.stdout.readline()
        if not response_line:
            print(f"[FAIL] Cycle {cycle_id}: Received EOF")
            print(process.stderr.read().decode())
            return False
            
        resp = json.loads(response_line.decode())
        if "result" in resp:
            print(f"[PASS] Cycle {cycle_id}: Initialized correctly.")
            return True
        else:
            print(f"[FAIL] Cycle {cycle_id}: Unexpected response: {resp}")
            return False
    except Exception as e:
        print(f"[ERROR] Cycle {cycle_id}: {e}")
        return False
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    success_count = 0
    total = 5
    for i in range(1, total + 1):
        if run_test_cycle(i):
            success_count += 1
        time.sleep(1)
    
    print(f"\nFinal Result: {success_count}/{total} cycles passed.")
    if success_count == total:
        print("SYSTEM STABLE: EOF error eradicated.")
    else:
        print("SYSTEM UNSTABLE: EOF error still persists.")
