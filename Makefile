.PHONY: verify-industrial verify-specs sdk

verify-industrial: verify-specs
	@echo "=== STARTING INDUSTRIAL AUDIT SUITE ==="
	@echo "[1/3] Running Swarm Race Integrity Test..."
	@python3 layers/l1_nervous/tests/industrial/test_swarm_race.py
	@echo "\n[2/3] Running Go Fencing Test (Auto-healing)..."
	@bash layers/l1_nervous/tests/industrial/test_fencing.sh
	@echo "\n[3/3] Running Deterministic E2E Flow Test (Error Propagation)..."
	@uv run --no-project --with pyarrow python3 layers/l1_nervous/tests/industrial/test_e2e_flow.py
	@echo "\n=== AUDIT SUITE COMPLETED ==="
	@echo "NOTA: El test [3/3] valida la propagación de errores cuando el servidor falla."

verify-specs:
	@echo "Validating Specs and Docs..."
	@python3 scripts/validate_specs_docs.py

sdk:
	@echo "Regenerating Typed SDKs..."
	@python3 scratch/generate_sdks.py
