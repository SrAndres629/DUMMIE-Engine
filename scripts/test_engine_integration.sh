#!/bin/bash
# DUMMIE Engine - Total Integration Test
# Verifies that L0, L1, and L2 can communicate via NATS.

set -e

echo "=== [TEST] Starting Engine Integration Test ==="

# 1. Start L1 Nervous (Go) in background
echo ">> Starting L1 Nervous..."
./bin/l1_nervous > l1.log 2>&1 &
L1_PID=$!

# 2. Start L0 Overseer (Elixir) in background
echo ">> Starting L0 Overseer..."
cd layers/l0_overseer && mix run --no-halt > ../../l0.log 2>&1 &
L0_PID=$!
cd ../..

# 3. Wait for logs to populate
echo ">> Waiting for causality synchronization (10s)..."
sleep 10

# 4. Check L1 Logs for Heartbeats
echo ">> Verifying L1 Heartbeats..."
if grep -q "Pulse: LamportTick" l1.log; then
    echo -e "\033[0;32m[OK] L1 is beating.\033[0m"
else
    echo -e "\033[0;31m[FAIL] L1 heartbeat not detected.\033[0m"
fi

# 5. Check L0 Logs for Validation
echo ">> Verifying L0 Validation..."
if grep -q "Latido validado" l0.log; then
    echo -e "\033[0;32m[OK] L0 is validating L1 pulse.\033[0m"
else
    echo -e "\033[0;31m[FAIL] L0 validation not detected.\033[0m"
fi

# 6. Cleanup
echo ">> Terminating test processes..."
kill $L1_PID $L0_PID || true
echo "=== [TEST] Integration Test Complete ==="
