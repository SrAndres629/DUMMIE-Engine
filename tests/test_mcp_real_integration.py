
import json
import os

def test_gateway_portability():
    with open("dummie_gateway_config.json", "r") as f:
        config = json.load(f)
    for server, cfg in config["mcpServers"].items():
        for arg in cfg.get("args", []):
            if isinstance(arg, str):
                assert not arg.startswith("/home/"), f"Hardcoded path found in {server}: {arg}"
                assert not arg.startswith("/media/"), f"Hardcoded path found in {server}: {arg}"
    print("✓ Gateway portability test passed")

def test_sqlite_schema_exists():
    path = ".aiwg/mcp/sqlite/schema.sql"
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r") as f:
        schema = f.read()
    assert "mcp_runtime_inventory" in schema
    assert "mcp_policy_audit" in schema
    print("✓ SQLite schema test passed")

def test_registry_versioned():
    path = ".aiwg/mcp/registry.yaml"
    assert os.path.exists(path), f"Missing {path}"
    print("✓ Registry versioned check passed")

if __name__ == "__main__":
    try:
        test_gateway_portability()
        test_sqlite_schema_exists()
        test_registry_versioned()
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        exit(1)
