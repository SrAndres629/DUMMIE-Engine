import pytest
import time
import tempfile
import numpy as np
from unittest.mock import AsyncMock, patch, MagicMock

from context_budget_tools import (
    ContextBudgetRouter,
    TIER_1_TOOLS,
    TIER_2_TOOLS,
    TIER_3_TOOLS,
    TIER_TOKEN_COST,
)
from smart_router import SmartRouter, DOMAIN_MAP
from semantic_cache import SemanticRouteCache, CacheEntry


class TestContextBudgetRouter:
    def setup_method(self):
        self.router = ContextBudgetRouter()

    def test_tier_1_for_small_budget(self):
        assert self.router.get_tier_for_budget(100) == 1
        assert self.router.get_tier_for_budget(TIER_TOKEN_COST[1]) == 1
        assert (
            self.router.get_tier_for_budget(TIER_TOKEN_COST[1] + TIER_TOKEN_COST[2] - 1)
            == 1
        )

    def test_tier_2_for_medium_budget(self):
        assert (
            self.router.get_tier_for_budget(TIER_TOKEN_COST[1] + TIER_TOKEN_COST[2])
            == 2
        )
        assert (
            self.router.get_tier_for_budget(
                TIER_TOKEN_COST[1] + TIER_TOKEN_COST[2] + TIER_TOKEN_COST[3] - 1
            )
            == 2
        )

    def test_tier_3_for_large_budget(self):
        total = TIER_TOKEN_COST[1] + TIER_TOKEN_COST[2] + TIER_TOKEN_COST[3]
        assert self.router.get_tier_for_budget(total) == 3
        assert self.router.get_tier_for_budget(total + 10000) == 3

    def test_zero_budget_returns_tier_1(self):
        assert self.router.get_tier_for_budget(0) == 1

    def test_negative_budget_returns_tier_1(self):
        assert self.router.get_tier_for_budget(-1) == 1
        assert self.router.get_tier_for_budget(-500) == 1

    def test_get_tools_for_budget_tier_1(self):
        tools = self.router.get_tools_for_budget(100)
        assert set(tools.keys()) == set(TIER_1_TOOLS.keys())

    def test_get_tools_for_budget_tier_2(self):
        budget = TIER_TOKEN_COST[1] + TIER_TOKEN_COST[2]
        tools = self.router.get_tools_for_budget(budget)
        expected = set(list(TIER_1_TOOLS.keys()) + list(TIER_2_TOOLS.keys()))
        assert set(tools.keys()) == expected

    def test_get_tools_for_budget_tier_3(self):
        budget = TIER_TOKEN_COST[1] + TIER_TOKEN_COST[2] + TIER_TOKEN_COST[3]
        tools = self.router.get_tools_for_budget(budget)
        expected = set(
            list(TIER_1_TOOLS.keys())
            + list(TIER_2_TOOLS.keys())
            + list(TIER_3_TOOLS.keys())
        )
        assert set(tools.keys()) == expected

    def test_tier_name(self):
        assert self.router.tier_name(100) == "core"
        assert (
            self.router.tier_name(TIER_TOKEN_COST[1] + TIER_TOKEN_COST[2]) == "extended"
        )
        total = TIER_TOKEN_COST[1] + TIER_TOKEN_COST[2] + TIER_TOKEN_COST[3]
        assert self.router.tier_name(total) == "specialized"

    def test_describe_tools(self):
        desc = self.router.describe_tools({"filesystem": ["read"]})
        assert "  filesystem.read" in desc

    def test_suggest_next_tier(self):
        assert self.router.suggest_next_tier(1, 0.8) != ""
        assert self.router.suggest_next_tier(2, 0.8) != ""
        assert self.router.suggest_next_tier(3, 0.9) == ""
        assert self.router.suggest_next_tier(1, 0.5) == ""
        assert self.router.suggest_next_tier(2, 0.3) == ""


class TestSmartRouter:
    def setup_method(self):
        self.router = SmartRouter()

    def test_empty_query_fast_fail(self):
        result = self.router._empty_result("")
        assert result["match"] is False
        assert result["domain"] is None

    @pytest.mark.asyncio
    async def test_empty_query_returns_immediately(self):
        result = await self.router.route("")
        assert result["match"] is False
        assert "Empty query" in result.get("message", "")

    @pytest.mark.asyncio
    async def test_whitespace_query_fast_fail(self):
        result = await self.router.route("   ")
        assert result["match"] is False

    def test_parse_json_markdown_fenced(self):
        raw = '```json\n{"domain": "shell", "confidence": 0.9}\n```'
        parsed = self.router._parse_json(raw)
        assert parsed is not None
        assert parsed["domain"] == "shell"
        assert parsed["confidence"] == 0.9

    def test_parse_json_raw(self):
        raw = '{"domain": "knowledge", "confidence": 0.8}'
        parsed = self.router._parse_json(raw)
        assert parsed is not None
        assert parsed["domain"] == "knowledge"

    def test_parse_json_with_surrounding_text(self):
        raw = 'Thinking...\n{"domain": "vcs", "tools": [], "confidence": 0.7}'
        parsed = self.router._parse_json(raw)
        assert parsed is not None
        assert parsed["domain"] == "vcs"

    def test_parse_json_invalid(self):
        assert self.router._parse_json("not json") is None
        assert self.router._parse_json("") is None
        assert self.router._parse_json("```\nbroken") is None

    def test_domain_map_covers_known_domains(self):
        expected = {
            "media_generation",
            "vcs",
            "workspace_io",
            "infrastructure",
            "knowledge",
            "shell",
        }
        assert set(DOMAIN_MAP.keys()) == expected

    def test_domain_map_has_valid_servers(self):
        for domain, config in DOMAIN_MAP.items():
            assert "servers" in config
            assert isinstance(config["servers"], list)
            assert len(config["servers"]) > 0
            assert "gateway" in config
            assert "port" in config

    def test_empty_result_format(self):
        result = self.router._empty_result("test query", error="something failed")
        assert result["match"] is False
        assert result["domain"] is None
        assert result["query"] == "test query"
        assert result["strategy"] == "smart_router"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_ollama_failure_returns_empty(self):
        with patch.object(
            self.router, "_ollama_generate", side_effect=Exception("Ollama down")
        ):
            with patch.object(self.router, "warm_kv_cache", AsyncMock()):
                result = await self.router.route("hello")
                assert result["match"] is False
                assert "Ollama down" in result.get("message", "")

    @pytest.mark.asyncio
    async def test_high_confidence_route(self):
        mock_resp = {
            "response": '{"domain": "shell", "action": "run", "tools": [{"server": "shell", "tool": "execute_command", "arguments": {}, "step_id": "1"}], "confidence": 0.95, "reasoning": "shell command"}'
        }
        with patch.object(
            self.router, "_ollama_generate", AsyncMock(return_value=mock_resp)
        ):
            with patch.object(self.router, "warm_kv_cache", AsyncMock()):
                result = await self.router.route("run ls -la")
                assert result["match"] is True
                assert result["domain"] == "shell"
                assert result["confidence"] >= 0.9
                assert result["strategy"] == "smart_router"

    @pytest.mark.asyncio
    async def test_low_confidence_triggers_fallback(self):
        mock_resp = {
            "response": '{"domain": "knowledge", "confidence": 0.3, "tools": []}'
        }
        with patch.object(
            self.router, "_ollama_generate", AsyncMock(return_value=mock_resp)
        ):
            with patch.object(self.router, "warm_kv_cache", AsyncMock()):
                with patch.object(
                    self.router, "_embedding_fallback", AsyncMock(return_value=None)
                ):
                    result = await self.router.route("tell me something")
                    assert result is not None

    @pytest.mark.asyncio
    async def test_unknown_domain_returns_empty(self):
        mock_resp = {
            "response": '{"domain": "unknown_domain", "confidence": 0.9, "tools": []}'
        }
        with patch.object(
            self.router, "_ollama_generate", AsyncMock(return_value=mock_resp)
        ):
            with patch.object(self.router, "warm_kv_cache", AsyncMock()):
                result = await self.router.route("do something weird")
                assert result["match"] is False
                assert "unknown" in result.get("message", "").lower()


def _make_fake_embed(dim: int = 384):
    """Returns a deterministic embedding for testing."""
    rng = np.random.default_rng(42)
    emb = rng.random(dim, dtype=np.float32)
    emb = emb / np.linalg.norm(emb)
    return emb


class TestSemanticRouteCache:
    @pytest.fixture
    def cache(self):
        return SemanticRouteCache(
            embedding_dim=384,
            default_ttl=300.0,
            similarity_threshold=0.90,
            max_entries=100,
        )

    @pytest.mark.asyncio
    async def test_empty_cache_returns_none(self, cache):
        with patch.object(cache, "_embed", AsyncMock(return_value=_make_fake_embed())):
            result = await cache.get("anything")
            assert result is None

    @pytest.mark.asyncio
    async def test_l1_exact_hit(self, cache):
        emb = _make_fake_embed()
        route = {"domain": "test", "match": True}
        with patch.object(cache, "_embed", AsyncMock(return_value=emb)):
            await cache.set("hello", route)
        with patch.object(cache, "_embed", AsyncMock()):
            result = await cache.get("hello")
            assert result == route

    @pytest.mark.asyncio
    async def test_l2_semantic_hit(self, cache):
        emb_a = _make_fake_embed()
        emb_b = emb_a * 0.98 + 0.02 * _make_fake_embed()
        emb_b = emb_b / np.linalg.norm(emb_b)

        route_a = {"domain": "knowledge", "match": True}
        with patch.object(cache, "_embed", AsyncMock(return_value=emb_a)):
            await cache.set("tell me a fact", route_a)

        with patch.object(cache, "_embed", AsyncMock(return_value=emb_b)):
            result = await cache.get("give me knowledge")
            assert result == route_a

    @pytest.mark.asyncio
    async def test_l2_semantic_miss(self, cache):
        far_emb = _make_fake_embed() * -1
        far_emb = far_emb / np.linalg.norm(far_emb)

        route_a = {"domain": "shell", "match": True}
        with patch.object(cache, "_embed", AsyncMock(return_value=_make_fake_embed())):
            await cache.set("run a command", route_a)

        with patch.object(cache, "_embed", AsyncMock(return_value=far_emb)):
            result = await cache.get("completely unrelated")
            assert result is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self):
        small = SemanticRouteCache(
            embedding_dim=384,
            default_ttl=300.0,
            similarity_threshold=0.90,
            max_entries=2,
        )
        with patch.object(small, "_embed", AsyncMock(return_value=_make_fake_embed())):
            await small.set("q1", {"id": 1})
            await small.set("q2", {"id": 2})
            await small.set("q3", {"id": 3})
            assert len(small._entries) == 2

    @pytest.mark.asyncio
    async def test_disabled_cache_skips_set(self):
        disabled = SemanticRouteCache(max_entries=0)
        with patch.object(
            disabled, "_embed", AsyncMock(return_value=_make_fake_embed())
        ):
            await disabled.set("anything", {"domain": "test"})
            assert len(disabled._entries) == 0

    @pytest.mark.asyncio
    async def test_ttl_expiry(self, cache):
        emb = _make_fake_embed()
        with patch.object(cache, "_embed", AsyncMock(return_value=emb)):
            await cache.set("stale_query", {"domain": "old"})
        cache._entries[0].timestamp = 0
        cache._entries[0].ttl = 1
        with patch.object(cache, "_embed", AsyncMock(return_value=_make_fake_embed())):
            result = await cache.get("stale_query")
            assert result is None

    @pytest.mark.asyncio
    async def test_set_update_existing(self, cache):
        emb = _make_fake_embed()
        with patch.object(cache, "_embed", AsyncMock(return_value=emb)):
            await cache.set("key", {"domain": "v1"})
            await cache.set("key", {"domain": "v2"})
        assert len(cache._entries) == 1
        assert cache._entries[0].route_result["domain"] == "v2"

    @pytest.mark.asyncio
    async def test_get_stats(self, cache):
        with patch.object(cache, "_embed", AsyncMock(return_value=_make_fake_embed())):
            await cache.set("q1", {"domain": "a"})
        stats = await cache.get_stats()
        assert stats["total_entries"] == 1

    @pytest.mark.asyncio
    async def test_save_load_roundtrip(self, cache):
        emb = _make_fake_embed()
        with patch.object(cache, "_embed", AsyncMock(return_value=emb)):
            await cache.set("persist_me", {"domain": "saved"})
        with tempfile.NamedTemporaryFile(suffix=".pkl") as f:
            await cache.save(f.name)
            fresh = SemanticRouteCache()
            await fresh.load(f.name)
            assert fresh._l1 is not None
            assert len(fresh._entries) == 1
            assert fresh._entries[0].route_result["domain"] == "saved"

    @pytest.mark.asyncio
    async def test_load_corrupted_file(self, cache):
        with tempfile.NamedTemporaryFile(suffix=".pkl") as f:
            f.write(b"not a valid pickle")
            f.flush()
            await cache.load(f.name)
            assert len(cache._entries) == 0

    @pytest.mark.asyncio
    async def test_load_nonexistent_file(self, cache):
        await cache.load("/tmp/nonexistent_file_xyz.pkl")
        assert len(cache._entries) == 0

    @pytest.mark.asyncio
    async def test_empty_query_in_set(self, cache):
        with patch.object(cache, "_embed", AsyncMock()):
            await cache.set("", {"domain": "test"})
            await cache.set("   ", {"domain": "test"})
        assert len(cache._entries) == 0
