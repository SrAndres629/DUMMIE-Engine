import os
import sys
import pytest
import shutil
import tempfile
from datetime import datetime, timezone
from brain.domain.governance.kernel_contracts import PreflightContext, ExecutionReceipt, PostflightMetrics
from brain.domain.context.capsule_models import TokenEconomyPolicy
from brain.application.ports.kernel_ports import KernelOperatingBoundaryPort
from brain.application.use_cases.guarded_execution import GuardedExecutionUseCase
from brain.application.use_cases.capsule_orchestration import CapsuleOrchestrationUseCase
from brain.infrastructure.adapters.kernel_adapters import RuntimeEntrypointGuard
from brain.infrastructure.adapters.capsule_adapters import IncrementalAstIndexerAdapter

class MockKernelBoundaryAdapter(KernelOperatingBoundaryPort):
    def __init__(self):
        self.receipts = []

    def acquire_preflight_context(self) -> PreflightContext:
        return PreflightContext(
            head_commit="dummy_commit_hash_123",
            current_pack="NONE",
            certainty_score=0.95,
            is_frozen=True,
            metrics_baseline={},
            active_warnings=[]
        )

    def commit_execution_receipt(self, receipt: ExecutionReceipt) -> None:
        self.receipts.append(receipt)

    def run_postflight_audit(self, receipt: ExecutionReceipt) -> PostflightMetrics:
        return PostflightMetrics(
            tokens_consumed=100,
            elapsed_ms=50,
            validation_status="PASSED",
            artifacts_generated=[]
        )

def test_kernel_preflight_mutation_gating():
    port = MockKernelBoundaryAdapter()
    use_case = GuardedExecutionUseCase(port)
    
    # Executing a read-only command works perfectly
    dummy_run = lambda: "SUCCESS"
    res = use_case.execute_guarded("read config data", dummy_run)
    assert res == "SUCCESS"
    assert len(port.receipts) == 1
    assert port.receipts[0].exit_code == 0
    assert port.receipts[0].state_mutated is True
    
    # Executing a mutation command raises PermissionError under frozen kernel
    with pytest.raises(PermissionError) as excinfo:
        use_case.execute_guarded("mutate database state", dummy_run)
    assert "Kernel is frozen" in str(excinfo.value)

def test_real_kernel_adapters_preflight_and_receipts():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Set up tmp state
        state_dir = os.path.join(tmpdir, "state")
        os.makedirs(state_dir, exist_ok=True)
        truth_file = os.path.join(state_dir, "current_truth.json")
        with open(truth_file, "w", encoding="utf-8") as f:
            f.write('{"current_pack": "NONE", "certainty_score": 0.95, "active_warnings": []}')
        
        adapter = RuntimeEntrypointGuard(aiwg_dir=tmpdir)
        preflight = adapter.acquire_preflight_context()
        assert preflight.current_pack == "NONE"
        assert preflight.is_frozen is True
        assert preflight.certainty_score == 0.95
        
        # Test receipt commit
        receipt = ExecutionReceipt(
            receipt_id="rec-abc-123",
            command_executed="test command",
            exit_code=0,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            duration_seconds=0.1,
            causal_witness_hash="dummy_witness",
            state_mutated=True
        )
        adapter.commit_execution_receipt(receipt)
        
        receipts_file = os.path.join(tmpdir, "reports", "receipts.jsonl")
        assert os.path.exists(receipts_file)
        with open(receipts_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) == 1
        data = json_data = json = None
        import json
        data = json.loads(lines[0])
        assert data["receipt_id"] == "rec-abc-123"
        assert data["command_executed"] == "test command"

def test_capsule_ast_indexing():
    with tempfile.TemporaryDirectory() as tmpdir:
        code_file = os.path.join(tmpdir, "sample.py")
        code_content = """
class MyFirstClass:
    def my_first_method(self):
        pass

def my_standalone_function():
    return True
"""
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code_content)
            
        adapter = IncrementalAstIndexerAdapter()
        nodes = adapter.index_source_ast([code_file])
        
        assert len(nodes) == 3
        # Class Def
        class_node = next(n for n in nodes if n.symbol_name == "MyFirstClass")
        assert class_node.symbol_type == "class"
        # Standalone function
        func_node = next(n for n in nodes if n.symbol_name == "my_standalone_function")
        assert func_node.symbol_type == "function"
        
        # Test capsule compilation
        use_case = CapsuleOrchestrationUseCase(adapter)
        policy = TokenEconomyPolicy(max_input_budget=500, max_output_budget=200, reserve_tokens=50)
        capsule = use_case.compile_capsule("PACK_3.2", [code_file], policy)
        
        assert capsule.target_pack == "PACK_3.2"
        assert capsule.token_budget_allocated == 500
        assert len(capsule.ast_nodes) == 3
