import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT.parents[0] / "l2_brain"
for path in (ROOT, L2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pytest

from capability_index import CapabilityIndex
from discovery_indexing import CapabilityIndexCache, index_remote_capabilities


class FakeRegistry:
    def __init__(self):
        self.servers = {
            "n8n": {
                "disabled": False,
                "profile": "automation",
                "capability_class": "workflow_automation",
                "rationale": "n8n workflows and webhooks",
            }
        }
        self.calls = 0

    def get_tools(self, server_name):
        assert server_name == "n8n"
        self.calls += 1
        return [
            {
                "name": "search_workflows",
                "description": "Search workflows and webhooks",
            }
        ]


class FakeProxyManager:
    def __init__(self):
        self.registry = FakeRegistry()


@pytest.mark.asyncio
async def test_remote_capabilities_are_indexed_from_sync_registry_tools():
    index = CapabilityIndex()
    proxy_manager = FakeProxyManager()

    await index_remote_capabilities(index, proxy_manager)

    automation_entries = index._capabilities.get("workflow_automation", [])
    assert any(entry["id"] == "remote.n8n" for entry in automation_entries)
    assert any(entry["id"] == "n8n.search_workflows" for entry in automation_entries)


class FakeTool:
    def __init__(self, name, description):
        self.name = name
        self.description = description


@pytest.mark.asyncio
async def test_capability_index_cache_reuses_index_until_signature_changes(tmp_path):
    cache = CapabilityIndexCache(skills_dirs=[tmp_path])
    proxy_manager = FakeProxyManager()
    local_tools = [FakeTool("brain_ping", "basic health")]

    first = await cache.get_index(local_tools, proxy_manager)
    second = await cache.get_index(local_tools, proxy_manager)

    assert first is second
    assert proxy_manager.registry.calls == 3

    proxy_manager.registry.servers["n8n"]["rationale"] = "updated rationale"

    third = await cache.get_index(local_tools, proxy_manager)

    assert third is not second
    assert proxy_manager.registry.calls == 5


class ColdStartRegistry:
    """Simulates a registry where tools appear after sidecars warm up."""

    def __init__(self):
        self.servers = {
            "n8n": {
                "disabled": False,
                "profile": "automation",
                "capability_class": "workflow_automation",
                "rationale": "n8n workflows and webhooks",
            }
        }
        self._tools_ready = False

    def get_tools(self, server_name):
        assert server_name == "n8n"
        if self._tools_ready:
            return [
                {
                    "name": "search_workflows",
                    "description": "Search workflows and webhooks",
                }
            ]
        return []


class ColdStartProxyManager:
    def __init__(self):
        self.registry = ColdStartRegistry()


@pytest.mark.asyncio
async def test_cache_rebuilds_when_sidecars_warm_up(tmp_path):
    """Signature must change when tools appear after cold start."""
    cache = CapabilityIndexCache(skills_dirs=[tmp_path])
    proxy_manager = ColdStartProxyManager()
    local_tools = [FakeTool("brain_ping", "basic health")]

    first = await cache.get_index(local_tools, proxy_manager)
    automation_entries = first._capabilities.get("workflow_automation", [])
    server_entries = [e for e in automation_entries if e["id"] == "remote.n8n"]
    tool_entries = [e for e in automation_entries if e["id"] == "n8n.search_workflows"]

    assert len(server_entries) == 1
    assert len(tool_entries) == 0

    proxy_manager.registry._tools_ready = True

    second = await cache.get_index(local_tools, proxy_manager)

    assert second is not first
    automation_entries = second._capabilities.get("workflow_automation", [])
    tool_entries = [e for e in automation_entries if e["id"] == "n8n.search_workflows"]
    assert len(tool_entries) == 1
