import subprocess
import json
import os
import sys

def test_mcp_init():
    root_dir = "/home/jorand/Escritorio/DUMMIE Engine"
    python_exe = os.path.join(root_dir, "layers/l2_brain/.venv/bin/python")
    server_script = os.path.join(root_dir, "layers/l1_nervous/mcp_server.py")
    
    env = os.environ.copy()
    env["DUMMIE_ROOT_DIR"] = root_dir
    env["DUMMIE_AIWG_DIR"] = os.path.join(root_dir, ".aiwg")
    env["DUMMIE_KUZU_DB_PATH"] = os.path.join(env["DUMMIE_AIWG_DIR"], "memory/loci.db")
    env["PYTHONPATH"] = f"{os.path.join(root_dir, 'layers/l2_brain')}:{os.path.join(root_dir, 'layers/l1_nervous')}"
    env["DUMMIE_MCP_CONFIG_PATH"] = os.path.join(root_dir, "dummie_agent_config.json")

    print(f"Starting server: {server_script}")
    process = subprocess.Popen(
        [python_exe, server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=False
    )

    # Prepare initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "TestClient", "version": "1.0.0"}
        }
    }
    
    request_str = json.dumps(init_request) + "\n"
    print("Sending initialize request...")
    process.stdin.write(request_str.encode())
    process.stdin.flush()

    # Read response
    print("Waiting for response...")
    try:
        response_line = process.stdout.readline()
        if not response_line:
            print("EOF received from server stdout!")
            print("--- STDERR ---")
            print(process.stderr.read().decode())
            return
        
        print(f"Response: {response_line.decode()}")
        response = json.loads(response_line.decode())
        print("Initialization successful!")
    except Exception as e:
        print(f"Error reading response: {e}")
        print("--- STDERR ---")
        print(process.stderr.read().decode())
    finally:
        process.terminate()

if __name__ == "__main__":
    test_mcp_init()
