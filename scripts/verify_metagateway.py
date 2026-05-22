#!/usr/bin/env python3
"""Verify MetaGateway routing for all 5 sub-gateways."""

import sys, json

sys.path.insert(0, "layers/l1_nervous")
from meta_router import MetaRouter


async def verify():
    router = MetaRouter()
    results = {"pass": 0, "fail": 0, "tests": []}

    async def test(name, query, expected_gateway, expected_match=True):
        r = await router.route(query)
        ok = r.get("match") == expected_match and r.get("gateway") == expected_gateway
        results["tests"].append(
            {
                "name": name,
                "query": query,
                "expected_gateway": expected_gateway,
                "actual_gateway": r.get("gateway"),
                "confidence": r.get("confidence"),
                "pass": ok,
            }
        )
        status = "✅" if ok else "❌"
        print(
            f"{status} {name}: {query} -> {r.get('gateway')} (conf={r.get('confidence')})"
        )
        if ok:
            results["pass"] += 1
        else:
            results["fail"] += 1

    # Media gateway
    await test("Media - image", "generar imagen", "media")
    await test("Media - video", "crear video promocional", "media")
    await test("Media - audio", "generar musica", "media")

    # Code gateway
    await test("Code - git", "git status", "code")
    await test("Code - filesystem", "leer archivo", "code")

    # Infra gateway
    await test("Infra - docker", "docker ps", "infra")
    await test("Infra - vercel", "deploy to vercel", "infra")

    # Knowledge gateway
    await test("Knowledge - sql", "consulta sql", "knowledge")
    await test("Knowledge - reasoning", "razonar sobre esto", "knowledge")

    # Shell gateway
    await test("Shell - command", "ejecutar comando shell", "shell")
    await test("Shell - browser", "navegar a youtube", "shell")

    # No match
    await test("No match", "cual es el clima", None, False)

    # Capabilities listing
    print("\n--- Capabilities ---")
    caps = router.list_all_capabilities()
    by_gateway = {}
    for c in caps:
        by_gateway.setdefault(c["gateway"], []).append(c["server"])
    for gw, servers in sorted(by_gateway.items()):
        print(f"  {gw} (port {caps[0]['port'] if caps else '?'}): {', '.join(servers)}")
    print(f"  Total capabilities: {len(caps)}")

    print(f"\n{'=' * 40}")
    print(
        f"Results: {results['pass']}/{len(results['tests'])} pass, {results['fail']} fail"
    )
    if results["fail"] == 0:
        print("✅ ALL TESTS PASS")
    else:
        print("❌ SOME TESTS FAILED")
    return results


async def verify_pipeline():
    """Test RoutingPipeline (exact + embedding + cross-encoder + LLM)."""
    sys.path.insert(0, "layers/l1_nervous")
    from routing import RoutingPipeline
    from routing.strategies.exact_match import ExactMatchStrategy
    from routing.strategies.embedding_match import EmbeddingMatchStrategy
    from routing.strategies.cross_encoder_rerank import CrossEncoderRerankStrategy
    from routing.strategies.llm_reasoning import LLMReasoningStrategy
    from routing.strategies.cot_reasoning import CoTReasoningStrategy
    from models.model_registry import ModelRegistry
    import time

    registry = ModelRegistry()
    pipeline = RoutingPipeline(
        [
            ExactMatchStrategy(),
            EmbeddingMatchStrategy(registry=registry),
            CrossEncoderRerankStrategy(registry=registry),
            CoTReasoningStrategy(registry=registry),
            LLMReasoningStrategy(registry=registry),
        ],
        threshold=0.5,
    )

    tests = [
        ("generar imagen", "media", True),
        ("git status", "code", True),
        ("docker ps", "infra", True),
        ("cual es el clima", None, False),
    ]
    passes = 0
    print("\n--- Pipeline Tests ---")
    for query, expected_gw, expected_match in tests:
        t0 = time.time()
        result = await pipeline.route(query)
        elapsed = (time.time() - t0) * 1000
        ok = result.match == expected_match and result.gateway == expected_gw
        s = "✅" if ok else "❌"
        print(
            f"{s} {query}: gw={result.gateway} conf={result.confidence:.3f} strategy={result.strategy} ({elapsed:.0f}ms)"
        )
        if ok:
            passes += 1
    print(f"Pipeline: {passes}/{len(tests)} pass")
    return passes == len(tests)


if __name__ == "__main__":
    import asyncio

    r = asyncio.run(verify())
    pipe_ok = asyncio.run(verify_pipeline())
    sys.exit(0 if r["fail"] == 0 and pipe_ok else 1)
