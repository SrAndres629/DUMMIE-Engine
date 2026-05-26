import os
from pathlib import Path

from layers.l1_nervous.capability_index import CapabilityIndex


def _skills_signature(skills_dirs: list[Path]) -> tuple[tuple[str, int], ...]:
    signature = []
    for base_dir in skills_dirs:
        if not base_dir.exists():
            signature.append((str(base_dir), -1))
            continue
        latest_mtime_ns = 0
        for skill_file in base_dir.rglob("SKILL.md"):
            latest_mtime_ns = max(latest_mtime_ns, skill_file.stat().st_mtime_ns)
        signature.append((str(base_dir), latest_mtime_ns))
    return tuple(signature)


def _server_signature(
    proxy_manager,
) -> tuple[tuple[str, tuple[tuple[str, str], ...]], ...]:
    signature = []
    for server_name, server_config in sorted(proxy_manager.registry.servers.items()):
        filtered = {
            key: str(value)
            for key, value in server_config.items()
            if key
            in {
                "disabled",
                "profile",
                "capability_class",
                "rationale",
                "command",
                "args",
                "env",
            }
        }
        tool_names = sorted(
            t.get("name", "") for t in proxy_manager.registry.get_tools(server_name)
        )
        filtered["_tools"] = ",".join(tool_names)
        signature.append((server_name, tuple(sorted(filtered.items()))))
    return tuple(signature)


def _local_tools_signature(local_tools) -> tuple[tuple[str, str], ...]:
    return tuple(
        sorted((tool.name, getattr(tool, "description", "")) for tool in local_tools)
    )


class CapabilityIndexCache:
    def __init__(self, skills_dirs: list[Path] | None = None):
        dummie_root = Path(
            os.environ.get("DUMMIE_ROOT", Path(__file__).resolve().parents[2])
        )
        default_dirs = [
            dummie_root / ".agents" / "skills",
            Path.home() / ".agents" / "skills" / "superpowers",
        ]
        self.skills_dirs = skills_dirs or default_dirs
        self._signature = None
        self._index = None

    async def get_index(self, local_tools, proxy_manager) -> CapabilityIndex:
        signature = (
            _local_tools_signature(local_tools),
            _server_signature(proxy_manager),
            _skills_signature(self.skills_dirs),
        )
        if signature == self._signature and self._index is not None:
            return self._index

        index = CapabilityIndex()
        for tool in local_tools:
            index._capabilities.setdefault("local_tools", []).append(
                {
                    "id": f"local.{tool.name}",
                    "name": tool.name,
                    "type": "local",
                    "description": getattr(tool, "description", ""),
                }
            )

        await index_remote_capabilities(index, proxy_manager)
        self._signature = signature
        self._index = index
        return index


async def index_remote_capabilities(index: CapabilityIndex, proxy_manager) -> None:
    for server_name, server_config in proxy_manager.registry.servers.items():
        if server_config.get("disabled", False):
            continue

        profile = server_config.get("profile", "default")
        capability_class = server_config.get("capability_class", "remote")
        rationale = server_config.get("rationale", "")
        index.add_mcp_server_config(server_name, profile, capability_class, rationale)

        try:
            remote_tools = proxy_manager.registry.get_tools(server_name)
            index.add_mcp_tools(server_name, remote_tools)
        except Exception:
            pass
