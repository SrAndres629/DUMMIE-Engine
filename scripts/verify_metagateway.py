#!/usr/bin/env python3
"""Verify MetaGateway routing for all 5 sub-gateways."""

import sys, json

sys.path.insert(0, "layers/l1_nervous")
from meta_router import MetaRouter


def verify():
    router = MetaRouter()
    results = {"pass": 0, "fail": 0, "tests": []}

    def test(name, query, expected_gateway, expected_match=True):
        r = router.route(query)
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
    test("Media - image", "generar imagen", "media")
    test("Media - video", "crear video promocional", "media")
    test("Media - audio", "generar musica", "media")

    # Code gateway
    test("Code - git", "git status", "code")
    test("Code - filesystem", "leer archivo", "code")

    # Infra gateway
    test("Infra - docker", "docker ps", "infra")
    test("Infra - vercel", "deploy to vercel", "infra")

    # Knowledge gateway
    test("Knowledge - sql", "consulta sql", "knowledge")
    test("Knowledge - reasoning", "razonar sobre esto", "knowledge")

    # Shell gateway
    test("Shell - command", "ejecutar comando shell", "shell")
    test("Shell - browser", "navegar a youtube", "shell")

    # No match
    test("No match", "cual es el clima", None, False)

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


if __name__ == "__main__":
    r = verify()
    sys.exit(0 if r["fail"] == 0 else 1)
