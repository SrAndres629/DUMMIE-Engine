import socket
import json
import yaml
import sys

def test_spawn():
    socket_path = "/tmp/dummied.sock"
    manifest_path = ".agents/manifests/investigator_swarm.yaml"
    
    with open(manifest_path, 'r') as f:
        manifest = yaml.safe_load(f)
    
    cmd = {
        "type": "SPAWN_SWARM",
        "goal": "Audit repository and spawn specialized fixers.",
        "id": "investigator_master_001",
        "manifest": manifest
    }
    
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect(socket_path)
        client.sendall(json.dumps(cmd).encode())
        response = client.recv(4096)
        print(f"Response: {response.decode()}")
    finally:
        client.close()

if __name__ == "__main__":
    test_spawn()
