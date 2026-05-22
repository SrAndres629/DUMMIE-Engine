import json, os
from pathlib import Path
from ..context_engine import ContextDimension


class EpisodicDimension(ContextDimension):
    name = "episodic"

    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            root = os.environ.get("DUMMIE_ROOT", "/media/datasets/DUMMIE Engine")
            memory_dir = os.path.join(root, ".aiwg", "memory")
        self._memory_path = Path(memory_dir)
        self._memory_path.mkdir(parents=True, exist_ok=True)

    async def collect(self) -> dict:
        memories = []
        for f in sorted(self._memory_path.glob("*.md"))[:3]:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")[:500]
                memories.append({"source": f.name, "content": content[:200]})
            except Exception:
                pass
        router_logs = (
            self._memory_path.parent.parent / "runtime" / "router_decisions.jsonl"
        )
        recent_decisions = []
        if router_logs.exists():
            try:
                with open(router_logs) as f:
                    for line in f.readlines()[-5:]:
                        recent_decisions.append(json.loads(line))
            except Exception:
                pass
        return {"memories": memories, "recent_decisions": recent_decisions}
