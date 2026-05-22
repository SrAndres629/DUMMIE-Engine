#!/usr/bin/env python3
"""Verify full RoutingPipeline (5 strategies) with Gemma 3."""

import sys, json, asyncio, time

sys.path.insert(0, "layers/l1_nervous")


async def verify_pipeline():
    from routing import RoutingPipeline
    from routing.strategies.exact_match import ExactMatchStrategy
    from routing.strategies.embedding_match import EmbeddingMatchStrategy
    from routing.strategies.cross_encoder_rerank import CrossEncoderRerankStrategy
    from routing.strategies.cot_reasoning import CoTReasoningStrategy
    from routing.strategies.llm_reasoning import LLMReasoningStrategy
    from models.model_registry import ModelRegistry

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
        ("generar imagen", "media", True, "exact"),
        ("git status", "code", True, "exact"),
        ("docker ps", "infra", True, "exact"),
        ("cual es el clima", None, False, None),
    ]

    passes = 0
    print(f"{'=' * 60}")
    print(f"Pipeline: {len(pipeline.strategies)} strategies")
    print(f"{'=' * 60}")

    for query, expected_gw, expected_match, expected_strategy in tests:
        t0 = time.time()
        result = await pipeline.route(query)
        elapsed = (time.time() - t0) * 1000

        ok = result.match == expected_match
        if expected_gw:
            ok = ok and result.gateway == expected_gw

        status = "✅" if ok else "❌"
        strategy_tag = f"strategy={result.strategy}" if result.match else "no-match"
        print(
            f"{status} {query:<30} -> gw={str(result.gateway or '-'):<10} conf={result.confidence:.3f} {strategy_tag} ({elapsed:.0f}ms)"
        )

        if result.match and hasattr(result, "reasoning") and result.reasoning:
            print(f"   reasoning: {result.reasoning[:100]}...")

        if ok:
            passes += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passes}/{len(tests)} pass")
    if passes == len(tests):
        print("✅ ALL TESTS PASS")
    else:
        print("❌ SOME TESTS FAILED")
    return passes == len(tests)


if __name__ == "__main__":
    ok = asyncio.run(verify_pipeline())
    sys.exit(0 if ok else 1)
