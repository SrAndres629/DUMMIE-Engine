from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DUMMIE_ROOT = Path("/opt/dummie-engine")


class GroupChatCoordinator:
    """
    Coordinates multiple agent roles — each with its OWN isolated session + KVCache.

    Jorge's vision clarified (m0312):
      - Cada agente (@planner, @builder, @reviewer, @overseer) mantiene
        su propia sesion, coherencia y contexto. Session + model = KVCache fijo.
      - El chat grupal solo los ORQUESTA: los llama cuando es necesario,
        muestra todo en UNA ventana CLI, sin abrir multiples terminales.
      - KVCache economico: misma sesion + mismo model + mismo system prompt
        = cache persistente entre interacciones.

    The coordinator:
      - Binds each agent to its own persistent session (SessionRole + SessionStore)
      - Routes messages to the appropriate agent session
      - Maintains a group chat log in .aiwg/chat/ for unified visibility
      - Activates role chains (planner -> builder -> reviewer) with handoffs
    """

    _ROLE_TO_SESSION_ROLE = {
        "planner": "plan",
        "builder": "build",
        "reviewer": "review",
        "overseer": "overseer",
    }

    AGENT_ROLES = {
        "planner": {
            "role": "plan",
            "model": "ollama/smallthinker:3b",
            "system_prompt": (
                "You are @planner, the strategic planning agent of the DUMMIE Engine. "
                "You have your OWN isolated session. You maintain your own KVCache and context. "
                "Your role: analyze requirements, break down tasks, create implementation plans, "
                "estimate effort, identify dependencies and risks. "
                "You work with @builder and @reviewer. When you finish planning, hand off to @builder. "
                "Always reference .aiwg specs and evidence. Be precise, structured, and canonical."
            ),
            "subagents": ["researcher", "designer"],
        },
        "builder": {
            "role": "build",
            "model": "ollama/smallthinker:3b",
            "system_prompt": (
                "You are @builder, the implementation agent of the DUMMIE Engine. "
                "You have your OWN isolated session. You maintain your own KVCache and context. "
                "Your role: write code, create files, run commands, execute the plan from @planner. "
                "Always follow specs and conventions. Write tests before code. "
                "Use canonical .aiwg paths. When done, hand off to @reviewer."
            ),
            "subagents": ["coder", "tester", "devops"],
        },
        "reviewer": {
            "role": "review",
            "model": "ollama/qwen3.5:0.8b",
            "system_prompt": (
                "You are @reviewer, the quality assurance agent of the DUMMIE Engine. "
                "You have your OWN isolated session. You maintain your own KVCache and context. "
                "Your role: review code, verify tests pass, check spec compliance, "
                "audit the output of @planner and @builder. "
                "If issues found, send back to @builder with specific feedback. "
                "If all clear, approve. Be thorough, skeptical, and evidence-based."
            ),
            "subagents": ["auditor", "validator"],
        },
        "overseer": {
            "role": "overseer",
            "model": "ollama/smallthinker:3b",
            "system_prompt": (
                "You are @overseer, the meta-coordinator of the DUMMIE Engine. "
                "You have your OWN isolated session. You maintain your own KVCache and context. "
                "Your role: observe the full pipeline, manage token budget, "
                "detect blockers, escalate to human when needed. "
                "You ensure @planner, @builder, and @reviewer work coherently "
                "without stepping on each other."
            ),
            "subagents": [],
        },
    }

    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.chat_dir = self.aiwg_root / "chat"
        self.chat_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.chat_dir / "group_state.json"
        self.queue_path = self.chat_dir / "message_queue.jsonl"
        self.log_path = self.chat_dir / "chat_log.jsonl"
        self.root_diary_path = DUMMIE_ROOT / "GROUP_CHAT.md"

        self.agent_sessions: dict[str, dict] = {}
        self._session_store = None
        self._ensure_agent_sessions()

    def _ensure_agent_sessions(self):
        from layers.l2_brain.session_store import SessionStore, SessionRole

        self._session_store = SessionStore(DUMMIE_ROOT)

        for agent_name, config in self.AGENT_ROLES.items():
            sr = SessionRole(config["role"])
            session = self._session_store.find_or_create_session(role=sr)
            contract = {
                "model": config["model"],
                "system_prompt": config["system_prompt"],
                "subagents": config["subagents"],
                "mode": config["role"],
                "kvcache_strategy": "reuse_persistent_session",
            }
            self._session_store.set_session_contract(session["session_id"], contract)
            self.agent_sessions[agent_name] = session
            logger.info(
                "Agent @%s bound to session %s (KVCache: %s)",
                agent_name,
                session["session_id"],
                session["session_id"],
            )

    def get_agent_session(self, role_name: str) -> dict | None:
        return self.agent_sessions.get(role_name)

    def route_to_agent(self, message: str, source: str = "jorge") -> dict:
        role = self.resolve_role(message)
        session = self.agent_sessions.get(role)
        agent_config = self.AGENT_ROLES.get(role, self.AGENT_ROLES["builder"])

        if session and self._session_store:
            sid = session["session_id"]
            self._session_store.append_event(
                sid,
                event_type="GROUP_INTAKE",
                summary=f"[{source}] {message[:300]}",
                data={
                    "source": source,
                    "role": role,
                    "model": agent_config["model"],
                },
            )

        self.log_interaction(
            role,
            f"[{source}] {message[:300]}",
            f"[routed to agent session {session['session_id'] if session else 'unknown'}]",
        )

        self._update_root_diary(source, role, message)

        return {
            "role": role,
            "agent": agent_config,
            "session_id": session["session_id"] if session else None,
            "model": agent_config["model"],
            "kvcache_key": f"{role}-{agent_config['model']}",
        }

    def process_group_message(self, message: str, source: str = "jorge") -> dict:
        routing = self.route_to_agent(message, source)
        role = routing["role"]
        chain = self.activate_role_chain(role)

        state = self.load_state()
        state["pipeline_status"] = "active"
        state["active_role"] = chain[0]
        state["pipeline_chain"] = chain
        state["last_message"] = {
            "source": source,
            "routed_to": role,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.save_state(state)

        handoff = self._generate_handoff(routing, chain)
        self.log_interaction("overseer", f"pipeline: {chain}", handoff)

        return {
            "type": "group_dispatch",
            "routing": routing,
            "chain": chain,
            "handoff_instructions": handoff,
        }

    def _generate_handoff(self, routing: dict, chain: list[str]) -> str:
        if len(chain) == 1:
            role = chain[0]
            return (
                f"@{role}: process this task independently in your session "
                f"({routing['session_id']}). No handoff needed."
            )

        handoff_lines = []
        for i, current_role in enumerate(chain):
            next_role = chain[i + 1] if i + 1 < len(chain) else None
            cfg = self.AGENT_ROLES.get(current_role, {})
            sid = (
                self.agent_sessions.get(current_role, {}).get("session_id")
                if self.agent_sessions.get(current_role)
                else "?"
            )
            if next_role:
                handoff_lines.append(
                    f"@{current_role} [{sid}]: work in your session, "
                    f"then hand off to @{next_role} via message queue."
                )
            else:
                handoff_lines.append(
                    f"@{current_role} [{sid}]: final step. "
                    f"Publish final result to the group chat log."
                )
        return " | ".join(handoff_lines)

    def compile_group_response(self, responses: list[dict[str, Any]]) -> str:
        lines = []
        for resp in responses:
            role = resp.get("role", "unknown").upper()
            sid = resp.get("session_id", "?")
            output = resp.get("output", "")
            lines.append(f"**[@{role}]** ({sid})\n{output}\n")
        return "\n---\n".join(lines)

    def close_all_agent_sessions(self) -> dict:
        results = {}
        for agent_name, session in self.agent_sessions.items():
            try:
                if self._session_store:
                    self._session_store.close_session(session["session_id"])
                    results[agent_name] = "closed"
            except Exception as e:
                results[agent_name] = f"error: {e}"
        self.agent_sessions = {}
        return results

    def _update_root_diary(self, source: str, role: str, message: str) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        entry = f"| {ts} | {source:>8} | {role:>10} | {message[:120]} |\n"
        with open(self.root_diary_path, "a", encoding="utf-8") as f:
            if f.tell() == 0:
                f.write("# DUMMIE Group Chat — Diary\n\n")
                f.write("| Timestamp | Source | Role | Message |\n")
                f.write("|-----------|--------|------|---------|\n")
            f.write(entry)

    def resolve_role(self, message: str) -> str:
        mentions = {
            "planner": [
                "@planner",
                "@plan",
                "planifica",
                "diseña",
                "arquitect",
                "diseñ",
                "plan",
                "spec",
            ],
            "builder": [
                "@builder",
                "@build",
                "construye",
                "implementa",
                "código",
                "code",
                "build",
                "escribe",
                "crea",
                "fix",
            ],
            "reviewer": [
                "@reviewer",
                "@review",
                "revisa",
                "audit",
                "verifica",
                "test",
                "prueba",
            ],
            "overseer": ["@overseer", "coordina", "supervisa", "orquest"],
        }

        for role, keywords in mentions.items():
            for kw in keywords:
                if kw.lower() in message.lower():
                    return role

        if any(
            w in message.lower()
            for w in [
                "plan",
                "task",
                "tarea",
                "especific",
                "spec",
                "diseño",
                "api",
                "design",
            ]
        ):
            return "planner"
        if any(
            w in message.lower()
            for w in ["review", "test", "check", "bug", "error", "fallo"]
        ):
            return "reviewer"

        return "builder"

    def activate_role_chain(self, entry_role: str) -> list[str]:
        chain_order = ["planner", "builder", "reviewer"]
        if entry_role not in chain_order:
            return [entry_role]

        idx = chain_order.index(entry_role)
        return chain_order[idx:]

    def get_agent_config(self, role_name: str) -> dict[str, Any]:
        return self.AGENT_ROLES.get(role_name, self.AGENT_ROLES["builder"])

    def enqueue_message(self, content: str, source_role: str, target_role: str) -> str:
        msg_id = f"msg-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        msg = {
            "msg_id": msg_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_role": source_role,
            "target_role": target_role,
            "content": content,
            "status": "queued",
        }
        with open(self.queue_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg, sort_keys=True) + "\n")
            f.flush()
            if hasattr(os, "fsync"):
                os.fsync(f.fileno())
        return msg_id

    def dequeue_messages(self, target_role: str) -> list[dict[str, Any]]:
        messages = []
        if not self.queue_path.exists():
            return messages
        with open(self.queue_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                    if (
                        msg.get("target_role") == target_role
                        and msg.get("status") == "queued"
                    ):
                        messages.append(msg)
                except json.JSONDecodeError:
                    pass
        return messages

    def mark_processed(self, msg_id: str) -> None:
        processed = []
        if self.queue_path.exists():
            with open(self.queue_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        msg = json.loads(line)
                        if msg.get("msg_id") == msg_id:
                            msg["status"] = "processed"
                        processed.append(msg)
                    except json.JSONDecodeError:
                        pass
        if processed:
            with open(self.queue_path, "w", encoding="utf-8") as f:
                for msg in processed:
                    f.write(json.dumps(msg, sort_keys=True) + "\n")

    def log_interaction(
        self,
        role: str,
        input_text: str,
        output_text: str,
        evidence_refs: list[str] | None = None,
    ) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "input_summary": input_text[:500],
            "output_summary": output_text[:500],
            "evidence_refs": evidence_refs or [],
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

    def save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, sort_keys=True)

    def load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            with open(self.state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "pipeline_status": "idle",
            "active_role": None,
            "blocked_by": None,
            "token_used": 0,
        }

    def compile_group_response(self, responses: list[dict[str, Any]]) -> str:
        lines = []
        for resp in responses:
            role = resp.get("role", "unknown").upper()
            output = resp.get("output", "")
            lines.append(f"**[@{role}]**\n{output}\n")
        return "\n---\n".join(lines)
