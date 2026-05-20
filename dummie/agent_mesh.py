from __future__ import annotations

# Spec: 203_agent_mesh_runtime

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dummie.paths import AIWG


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class AgentMeshProfile:
    agent_id: str
    display_name: str
    harness: str
    preferred_roles: list[str]
    model_profile: str
    capabilities: list[str] = field(
        default_factory=lambda: ["ANALYZE_PLAN", "SPEC_AUTHORING", "PATCH_PROPOSAL", "WORKSPACE_WRITE"]
    )
    inputs: list[str] = field(default_factory=lambda: ["inbox", "control"])
    outputs: list[str] = field(default_factory=lambda: ["outbox", "handoff"])


class AgentMeshRuntime:
    """
    File-backed coordination runtime for DUMMIE-controlled agentic CLIs.

    The first version is intentionally deterministic: it creates native boot
    bundles and mailbox channels without launching external CLIs. Process spawn
    and shutdown can be layered on top of the same manifest.
    """

    DEFAULT_AGENTS = [
        AgentMeshProfile(
            agent_id="codex_cli",
            display_name="Codex CLI",
            harness="codex",
            preferred_roles=["implementation", "tests", "repo_ops"],
            model_profile="code_surgical",
        ),
        AgentMeshProfile(
            agent_id="gemini_cli",
            display_name="Gemini CLI",
            harness="gemini",
            preferred_roles=["critique", "large_context_review", "planning"],
            model_profile="broad_context_review",
        ),
        AgentMeshProfile(
            agent_id="antigravity",
            display_name="Antigravity",
            harness="antigravity",
            preferred_roles=["ide_navigation", "multi_file_refactor", "review"],
            model_profile="ide_agent",
        ),
        AgentMeshProfile(
            agent_id="opencode",
            display_name="OpenCode",
            harness="opencode",
            preferred_roles=["local_cli", "model_routing", "patch_generation"],
            model_profile="local_or_router",
        ),
    ]

    def __init__(self, aiwg_root: str | Path = AIWG):
        self.aiwg_root = Path(aiwg_root)
        self.mesh_root = self.aiwg_root / "agent_mesh"
        self.agents_root = self.mesh_root / "agents"
        self.manifest_path = self.mesh_root / "manifest.json"
        self.events_path = self.mesh_root / "events.jsonl"

    def bootstrap_mesh(self) -> dict[str, Any]:
        self.agents_root.mkdir(parents=True, exist_ok=True)
        agents: dict[str, Any] = {}
        for profile in self.DEFAULT_AGENTS:
            agents[profile.agent_id] = self._bootstrap_agent(profile)

        manifest = {
            "runtime_id": "dummie_agent_mesh",
            "schema_version": "dummie.agent_mesh.v1",
            "generated_at": _utc_now(),
            "agents": agents,
            "dynamic_lifecycle": {
                "future_spawn_close_enabled": False,
                "model_specific_boot_profiles": True,
                "spawn_policy": "manual_until_process_supervision_is_verified",
            },
        }
        self._write_json(self.manifest_path, manifest)
        self._append_event("mesh_bootstrap", {"agent_count": len(agents)})
        return manifest

    def status(self) -> dict[str, Any]:
        manifest = self._load_manifest()
        agents = manifest.get("agents", {})
        return {
            "runtime_id": manifest.get("runtime_id", "dummie_agent_mesh"),
            "agent_count": len(agents),
            "agents": sorted(agents),
            "channels_per_agent": {"inputs": 2, "outputs": 2},
            "dynamic_lifecycle": manifest.get("dynamic_lifecycle", {}),
            "manifest_path": str(self.manifest_path),
        }

    def send_message(self, sender: str, recipient: str, topic: str, body: str) -> dict[str, Any]:
        manifest = self._load_manifest()
        self._require_agent(manifest, sender)
        self._require_agent(manifest, recipient)
        message = {
            "message_id": str(uuid.uuid4()),
            "created_at": _utc_now(),
            "sender": sender,
            "recipient": recipient,
            "topic": topic,
            "body": body,
            "channel": "inbox",
            "status": "queued",
        }
        self._append_channel(recipient, "inbox", message)
        self._append_channel(sender, "outbox", message)
        self._append_event("message_queued", {k: message[k] for k in ("message_id", "sender", "recipient", "topic")})
        return message

    def read_channel(self, agent_id: str, channel: str) -> list[dict[str, Any]]:
        if channel not in {"inbox", "control", "outbox", "handoff"}:
            raise ValueError(f"unsupported channel: {channel}")
        path = self.agents_root / agent_id / f"{channel}.jsonl"
        if not path.exists():
            return []
        records = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
        return records

    def _bootstrap_agent(self, profile: AgentMeshProfile) -> dict[str, Any]:
        agent_root = self.agents_root / profile.agent_id
        agent_root.mkdir(parents=True, exist_ok=True)
        for channel in [*profile.inputs, *profile.outputs]:
            (agent_root / f"{channel}.jsonl").touch(exist_ok=True)

        system_prompt_path = agent_root / "system_prompt.md"
        hook_manifest_path = agent_root / "hooks.json"
        self._write_text(system_prompt_path, self._render_system_prompt(profile))
        self._write_json(hook_manifest_path, self._render_hooks(profile))

        data = asdict(profile)
        data["boot_bundle"] = {
            "system_prompt_path": str(system_prompt_path),
            "hook_manifest_path": str(hook_manifest_path),
            "channels_root": str(agent_root),
        }
        return data

    def _render_system_prompt(self, profile: AgentMeshProfile) -> str:
        roles = ", ".join(profile.preferred_roles)
        capabilities = ", ".join(profile.capabilities)
        return (
            f"# DUMMIE Agent Mesh Boot: {profile.display_name}\n\n"
            "You are a DUMMIE Engine worker node connected to the DUMMIE Agent Mesh.\n"
            "Load the universal session contract, obey specs, preserve evidence, and communicate through your mesh channels.\n\n"
            f"- agent_id: {profile.agent_id}\n"
            f"- harness: {profile.harness}\n"
            f"- preferred_roles: {roles}\n"
            f"- capabilities: {capabilities}\n"
            "- inputs: inbox, control\n"
            "- outputs: outbox, handoff\n"
            "- commit_push_policy: only after required verification passes\n"
        )

    def _render_hooks(self, profile: AgentMeshProfile) -> dict[str, Any]:
        return {
            "agent_id": profile.agent_id,
            "preflight": [
                "load .aiwg/session_contracts/UNIVERSAL_AGENT_SESSION_CONTRACT.md",
                "load agent system_prompt.md",
                "check inbox",
                "run scope and verification planning",
            ],
            "postflight": [
                "write outbox summary",
                "write handoff when another agent must continue",
                "record verification evidence",
            ],
            "blocked_actions": ["secret_exfiltration", "destructive_git_without_approval", "unverified_commit_push"],
        }

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return self.bootstrap_mesh()
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def _require_agent(self, manifest: dict[str, Any], agent_id: str) -> None:
        if agent_id not in manifest.get("agents", {}):
            raise ValueError(f"unknown agent: {agent_id}")

    def _append_channel(self, agent_id: str, channel: str, payload: dict[str, Any]) -> None:
        path = self.agents_root / agent_id / f"{channel}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True, sort_keys=True) + "\n")

    def _append_event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.mesh_root.mkdir(parents=True, exist_ok=True)
        event = {"event_type": event_type, "created_at": _utc_now(), "payload": payload}
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=True, sort_keys=True) + "\n")

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8")

    def _write_text(self, path: Path, payload: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
