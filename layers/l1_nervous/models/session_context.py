import time, json, os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SessionContext:
    session_id: str = ""
    active_project: str = ""
    recent_queries: list[str] = field(default_factory=list)
    recent_domains: list[str] = field(default_factory=list)
    created_at: float = 0.0
    last_query_at: float = 0.0
    memory_tokens: list[str] = field(default_factory=list)


class SessionManager:
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            root = os.environ.get("DUMMIE_ROOT", "/media/datasets/DUMMIE Engine")
            memory_dir = os.path.join(root, ".aiwg", "memory")
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def get_active_project(self) -> str:
        cwd = os.getcwd()
        if "DUMMIE" in cwd:
            return "dummie-engine"
        if "open-generative-ai" in cwd:
            return "open-generative-ai"
        return "unknown"

    def load_memory_tokens(self) -> list[str]:
        tokens = []
        for f in sorted(self.memory_dir.glob("*.md"))[:5]:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")[:500]
                tokens.append(content)
            except Exception:
                pass
        return tokens

    def create_session(self, session_id: str = None) -> SessionContext:
        import uuid

        return SessionContext(
            session_id=session_id or str(uuid.uuid4())[:8],
            active_project=self.get_active_project(),
            created_at=time.time(),
            last_query_at=time.time(),
            memory_tokens=self.load_memory_tokens(),
        )

    def update_session(self, ctx: SessionContext, query: str = "", domain: str = ""):
        ctx.last_query_at = time.time()
        if query:
            ctx.recent_queries.append(query)
            if len(ctx.recent_queries) > 10:
                ctx.recent_queries.pop(0)
        if domain:
            ctx.recent_domains.append(domain)
            if len(ctx.recent_domains) > 10:
                ctx.recent_domains.pop(0)

    def enrich_prompt(self, ctx: SessionContext) -> str:
        parts = []
        if ctx.active_project:
            parts.append(f"Proyecto activo: {ctx.active_project}")
        if ctx.recent_queries:
            parts.append(f"Ultimas consultas: {', '.join(ctx.recent_queries[-3:])}")
        if ctx.recent_domains:
            parts.append(f"Dominios recientes: {', '.join(ctx.recent_domains[-3:])}")
        if ctx.memory_tokens:
            memory_snippet = ctx.memory_tokens[0][:200] if ctx.memory_tokens else ""
            parts.append(f"Contexto de memoria: {memory_snippet}")
        return "\n".join(parts)
