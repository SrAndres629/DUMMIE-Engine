from __future__ import annotations

import json

from dummie.agent_mesh import AgentMeshRuntime


def test_agent_mesh_bootstrap_creates_native_cli_contracts(tmp_path):
    runtime = AgentMeshRuntime(aiwg_root=tmp_path / ".aiwg")

    manifest = runtime.bootstrap_mesh()

    assert manifest["runtime_id"] == "dummie_agent_mesh"
    assert set(manifest["agents"]) == {"codex_cli", "gemini_cli", "antigravity", "opencode"}
    for agent_id, agent in manifest["agents"].items():
        assert agent["inputs"] == ["inbox", "control"]
        assert agent["outputs"] == ["outbox", "handoff"]
        assert "ANALYZE_PLAN" in agent["capabilities"]
        assert agent["boot_bundle"]["system_prompt_path"].endswith(f"{agent_id}/system_prompt.md")
        assert agent["boot_bundle"]["hook_manifest_path"].endswith(f"{agent_id}/hooks.json")

    codex_prompt = tmp_path / ".aiwg" / "agent_mesh" / "agents" / "codex_cli" / "system_prompt.md"
    assert "DUMMIE Agent Mesh" in codex_prompt.read_text(encoding="utf-8")


def test_agent_mesh_routes_messages_to_peer_inbox_and_sender_outbox(tmp_path):
    runtime = AgentMeshRuntime(aiwg_root=tmp_path / ".aiwg")
    runtime.bootstrap_mesh()

    message = runtime.send_message(
        sender="codex_cli",
        recipient="gemini_cli",
        topic="handoff",
        body="Audit this contract and return risks.",
    )

    assert message["sender"] == "codex_cli"
    assert message["recipient"] == "gemini_cli"
    assert message["channel"] == "inbox"

    inbox_records = runtime.read_channel("gemini_cli", "inbox")
    outbox_records = runtime.read_channel("codex_cli", "outbox")

    assert inbox_records[-1]["message_id"] == message["message_id"]
    assert outbox_records[-1]["message_id"] == message["message_id"]


def test_agent_mesh_status_reports_open_slots_for_dynamic_future_agents(tmp_path):
    runtime = AgentMeshRuntime(aiwg_root=tmp_path / ".aiwg")
    runtime.bootstrap_mesh()

    status = runtime.status()

    assert status["agent_count"] == 4
    assert status["dynamic_lifecycle"]["future_spawn_close_enabled"] is False
    assert status["dynamic_lifecycle"]["model_specific_boot_profiles"] is True
    assert status["channels_per_agent"] == {"inputs": 2, "outputs": 2}
