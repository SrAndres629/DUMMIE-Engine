import sys
import os
from unittest.mock import MagicMock

# Force absolute path
sys.path.append(os.getcwd())

def test_final_audit():
    print("=== DUMMIE INDUSTRIAL AUDIT v3.0 ===")
    
    # 1. Import check
    try:
        from layers.l2_brain.daemon import DummieDaemon
        from layers.l2_brain.event_bus import AsyncEventBus
        print("[PASS] Core imports successful")
    except Exception as e:
        print(f"[FAIL] Core imports failed: {e}")
        return

    # 2. Status check
    eb = MagicMock(spec=AsyncEventBus)
    gw = MagicMock()
    daemon = DummieDaemon(ledger_path="audit_ledger.json", mcp_gateway=gw, event_bus=eb)
    
    if daemon.metacognition_status == "READY":
        print(f"[PASS] Metacognition Status: {daemon.metacognition_status}")
    else:
        print(f"[FAIL] Metacognition Status: {daemon.metacognition_status} (Error: {daemon.metacognition_error})")

    # 3. Artifact check
    artifacts = [
        ".aiwg/reports/metagateway_token_savings_benchmark.json",
        ".aiwg/reports/metagateway_token_savings_benchmark.md",
        "doc/specs/71_metagateway_sensor_first_policy.md"
    ]
    for art in artifacts:
        if os.path.exists(art):
            print(f"[PASS] Artifact exists: {art}")
        else:
            print(f"[FAIL] Artifact missing: {art}")

    # 4. Policy check
    try:
        from layers.l2_brain.metagateway_policy import SensorFirstPolicy, Purpose, DirectReadRequest
        policy = SensorFirstPolicy()
        req = DirectReadRequest(purpose=Purpose.CONCEPT_DISCOVERY)
        decision = policy.evaluate(req)
        print(f"[PASS] Policy evaluation: {decision}")
    except Exception as e:
        print(f"[FAIL] Policy logic failed: {e}")

    print("=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    test_final_audit()
