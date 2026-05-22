import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger("dummie-mcp.context-enricher")


@dataclass
class SessionContext:
    recent_queries: List[str] = field(default_factory=list)
    active_mcps: List[str] = field(default_factory=list)
    active_project: str = ""
    memory_tokens: List[str] = field(default_factory=list)
    session_id: str = ""
    environment: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "recent_queries": self.recent_queries[-5:],
            "active_mcps": self.active_mcps,
            "active_project": self.active_project,
            "memory_tokens": self.memory_tokens,
            "session_id": self.session_id,
        }


class ContextEnricher:
    def __init__(self):
        self._context_cache: Dict[str, SessionContext] = {}
        self._session_queries: Dict[str, List[str]] = {}

    def get_context(self, session_id: str = "default") -> SessionContext:
        if session_id in self._context_cache:
            return self._context_cache[session_id]

        ctx = SessionContext(session_id=session_id)
        ctx.active_project = self._detect_active_project()
        ctx.environment = self._get_env_info()
        ctx.active_mcps = self._get_active_mcps()
        ctx.memory_tokens = self._load_memory_tokens()

        self._context_cache[session_id] = ctx
        return ctx

    def record_query(self, query: str, session_id: str = "default"):
        if session_id not in self._session_queries:
            self._session_queries[session_id] = []
        self._session_queries[session_id].append(query)
        if session_id in self._context_cache:
            self._context_cache[session_id].recent_queries = self._session_queries[
                session_id
            ]

    def _detect_active_project(self) -> str:
        cwd = os.environ.get("PWD", "")
        home = os.path.expanduser("~")
        if cwd.startswith(home):
            rel = os.path.relpath(cwd, home)
            parts = rel.split(os.sep)
            return parts[0] if parts else "unknown"
        return os.path.basename(cwd) if cwd else "unknown"

    def _get_env_info(self) -> dict:
        return {
            "cwd": os.environ.get("PWD", ""),
            "user": os.environ.get("USER", ""),
            "shell": os.environ.get("SHELL", ""),
        }

    def _get_active_mcps(self) -> List[str]:
        dummie_root = os.environ.get(
            "DUMMIE_ROOT",
            "/media/datasets/DUMMIE Engine",
        )
        config_path = os.path.join(dummie_root, "dummie_gateway_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    cfg = json.load(f)
                return list(cfg.get("mcpServers", {}).keys())
            except Exception:
                pass
        return []

    def _load_memory_tokens(self) -> List[str]:
        dummie_root = os.environ.get(
            "DUMMIE_ROOT",
            "/media/datasets/DUMMIE Engine",
        )
        mem_file = os.path.join(dummie_root, ".aiwg", "memory", "recent_tokens.json")
        if os.path.exists(mem_file):
            try:
                with open(mem_file) as f:
                    data = json.load(f)
                return data.get("tokens", [])
            except Exception:
                pass
        return []
