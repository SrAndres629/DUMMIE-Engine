from __future__ import annotations

from dummie.guardrails import ContextBanPolicy


def test_context_ban_blocks_runtime_memory_db() -> None:
    reason = ContextBanPolicy.classify(".aiwg/memory/loci.db")
    assert reason is not None


def test_context_ban_blocks_node_modules() -> None:
    reason = ContextBanPolicy.classify("node_modules/pkg/index.js")
    assert reason is not None
