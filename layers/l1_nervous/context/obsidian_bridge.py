import json, os, logging
from pathlib import Path

logger = logging.getLogger("dummie-mcp.context.obsidian")


class ObsidianBridge:
    def __init__(self, vault_path: str = None):
        self._vault_path = vault_path or os.environ.get("OBSIDIAN_VAULT", "")
        self._mcp_available = False

    async def check_mcp(self) -> bool:
        try:
            import subprocess

            r = subprocess.run(
                ["npx", "-y", "@nicholasgriffintn/mcp-obsidian", "--help"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self._mcp_available = r.returncode == 0
        except Exception:
            self._mcp_available = False
        return self._mcp_available

    async def search_notes(self, query: str, max_results: int = 3) -> list[dict]:
        if not self._vault_path:
            return []
        vault = Path(self._vault_path)
        if not vault.exists():
            return []
        results = []
        for f in vault.rglob("*.md"):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if query.lower() in content.lower():
                    results.append(
                        {"path": str(f.relative_to(vault)), "content": content[:300]}
                    )
                    if len(results) >= max_results:
                        break
            except Exception:
                pass
        return results

    async def read_note(self, path: str) -> str:
        if not self._vault_path:
            return ""
        target = Path(self._vault_path) / path
        if target.exists():
            return target.read_text(encoding="utf-8", errors="ignore")
        return ""

    async def get_recent_context(self) -> dict:
        if not self._vault_path:
            return {"status": "no_vault_configured"}
        vault = Path(self._vault_path)
        if not vault.exists():
            return {"status": "vault_not_found", "path": self._vault_path}
        recent = sorted(
            vault.rglob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True
        )[:3]
        return {
            "vault_path": self._vault_path,
            "total_notes": len(list(vault.rglob("*.md"))),
            "recent_notes": [
                {"name": f.stem, "modified": f.stat().st_mtime} for f in recent
            ],
        }
