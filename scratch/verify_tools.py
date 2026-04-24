import subprocess
import json
import os

def test_tool_discovery():
    root_dir = "/home/jorand/Escritorio/DUMMIE Engine"
    python_exe = os.path.join(root_dir, "layers/l2_brain/.venv/bin/python")
    server_script = os.path.join(root_dir, "layers/l1_nervous/mcp_server.py")
    
    env = os.environ.copy()
    env["DUMMIE_ROOT_DIR"] = root_dir
    env["DUMMIE_AIWG_DIR"] = os.path.join(root_dir, ".aiwg")
    env["PYTHONPATH"] = f"{os.path.join(root_dir, 'layers/l2_brain')}:{os.path.join(root_dir, 'layers/l1_nervous')}"
    
    process = subprocess.Popen(
        [python_exe, server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    # Initialize
    process.stdin.write((json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "Audit", "version": "1.0"}}
    }) + "\n").encode())
    process.stdin.flush()
    process.stdout.readline() # Consume init response

    # List tools
    process.stdin.write((json.dumps({
        "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}
    }) + "\n").encode())
    process.stdin.flush()
    
    response_line = process.stdout.readline()
    process.terminate()
    
    if response_line:
        resp = json.loads(response_line.decode())
        tools = resp.get("result", {}).get("tools", [])
        print(f"Discovered {len(tools)} tools:")
        for t in tools:
            print(f"- {t['name']}")
        return len(tools) > 0
    return False

if __name__ == "__main__":
    test_tool_discovery()
