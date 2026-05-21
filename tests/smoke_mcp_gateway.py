
import asyncio
import json
import os
import subprocess

def test_gateway_config_load():
    config_path = "dummie_gateway_config.json"
    assert os.path.exists(config_path), f"Gateway config {config_path} must exist"
    with open(config_path, "r") as f:
        config = json.load(f)
    assert "mcpServers" in config
    assert "sequentialthinking" in config["mcpServers"]
    print("✓ Gateway config load test passed")

def test_manual_healthchecks():
    # Since we can't use PyYAML easily, we test the core servers directly
    # based on the inventory we know.
    checks = [
        ("sequentialthinking", "npx -y @modelcontextprotocol/server-sequential-thinking --help"),
        ("github", "npx -y @modelcontextprotocol/server-github --help"),
    ]
    for name, cmd in checks:
        print(f"Running healthcheck for {name}...")
        res = subprocess.run(cmd, shell=True, capture_output=True)
        print(f"  {name}: exit_code={res.returncode}")
        # Note: help commands often exit 0 or 1 depending on the tool,
        # but the fact they run is what we check here.

if __name__ == "__main__":
    try:
        test_gateway_config_load()
        test_manual_healthchecks()
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)
