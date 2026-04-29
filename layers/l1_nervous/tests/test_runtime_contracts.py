import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
L2 = ROOT.parents[0] / "l2_brain"
L4 = ROOT.parents[0] / "l4_edge"
for path in (ROOT, L2, L4):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from resources import register_resources
from runtime_paths import resolve_dummied_socket_path
from file_watcher import FileWatcher


class FakeMCP:
    def __init__(self):
        self.resources = {}

    def resource(self, uri):
        def decorator(fn):
            self.resources[uri] = fn
            return fn

        return decorator


def test_resolve_dummied_socket_path_uses_explicit_override(monkeypatch):
    monkeypatch.setenv("DUMMIE_DUMMIED_SOCKET_PATH", "/tmp/explicit-dummied.sock")
    monkeypatch.delenv("DUMMIE_AIWG_DIR", raising=False)

    assert resolve_dummied_socket_path("/repo") == Path("/tmp/explicit-dummied.sock")


def test_resolve_dummied_socket_path_uses_canonical_aiwg_dir(monkeypatch, tmp_path):
    monkeypatch.delenv("DUMMIE_DUMMIED_SOCKET_PATH", raising=False)
    monkeypatch.setenv("DUMMIE_AIWG_DIR", str(tmp_path / ".aiwg"))

    assert resolve_dummied_socket_path("/repo") == tmp_path / ".aiwg" / "sockets" / "dummied.sock"


def test_brain_identity_uses_identity_md_fields_as_agent_identity(tmp_path):
    (tmp_path / ".aiwg").mkdir()
    (tmp_path / "IDENTITY.md").write_text(
        "# IDENTITY.md\n\n"
        "- **Name:** Test Pilot\n"
        "- **Creature:** Runtime Ghost\n"
        "- **Vibe:** Exacting\n"
        "- **Emoji:** :satellite:\n"
        "- **Avatar:** docs/assets/test-pilot.png\n"
    )
    (tmp_path / ".aiwg" / "identity.json").write_text(
        json.dumps(
            {
                "project_name": "DUMMIE Engine",
                "personality_profile": {"mood": "MISSION_CRITICAL"},
                "historical_decision_context": {"primary_language_focus": ["Python"]},
            }
        )
    )

    mcp = FakeMCP()
    register_resources(mcp, lambda: None, lambda: None, str(tmp_path))

    payload = json.loads(mcp.resources["brain://identity"]())
    profile = payload["personality_profile"]
    agent_identity = payload["agent_identity"]

    assert payload["project_name"] == "DUMMIE Engine"
    assert profile["agent_name"] == "Test Pilot"
    assert profile["creature"] == "Runtime Ghost"
    assert profile["vibe"] == "Exacting"
    assert profile["emoji"] == ":satellite:"
    assert profile["avatar"] == "docs/assets/test-pilot.png"
    assert agent_identity["name"] == "Test Pilot"
    assert payload["identity_sources"]["agent_identity"] == "IDENTITY.md"


def test_launchers_pin_l0_to_canonical_aiwg_socket_contract():
    factory = (REPO_ROOT / "scripts" / "factory_up.sh").read_text()
    runtime = (REPO_ROOT / "scripts" / "sovereign_runtime.sh").read_text()
    shutdown = (REPO_ROOT / "scripts" / "shutdown_factory.sh").read_text()

    assert "sockets/dummied.sock" in factory
    assert 'DUMMIE_AIWG_DIR="$AIWG_DIR"' in factory
    assert 'DUMMIE_AIWG_DIR="$AIWG_DIR"' in runtime
    assert "$DUMMIED_SOCKET_PATH" in factory
    assert "$DUMMIED_SOCKET_PATH" in shutdown


@pytest.mark.asyncio
async def test_file_watcher_is_explicitly_disabled_until_implemented():
    watcher = FileWatcher("/tmp/dummie-watch")

    result = await watcher.watch_forever()

    assert watcher.enabled is False
    assert result == "DISABLED_PENDING_IMPLEMENTATION"
