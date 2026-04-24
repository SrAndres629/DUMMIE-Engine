.PHONY: verify-industrial

verify-industrial:
	@echo "=== STARTING INDUSTRIAL AUDIT SUITE ==="
	@echo "[1/2] Running Swarm Race Integrity Test..."
	@python3 layers/l1_nervous/tests/industrial/test_swarm_race.py
	@echo "\n[2/2] Running Deterministic E2E Flow Test..."
	@uv run --no-project --with pyarrow python3 layers/l1_nervous/tests/industrial/test_e2e_flow.py
	@echo "\n=== AUDIT SUITE COMPLETED ==="
