import os
import json
import subprocess
from datetime import datetime, timezone
from brain.application.ports.kernel_ports import KernelOperatingBoundaryPort
from brain.domain.governance.kernel_contracts import PreflightContext, ExecutionReceipt, PostflightMetrics

class RuntimeEntrypointGuard(KernelOperatingBoundaryPort):
    def __init__(self, aiwg_dir: str = ".aiwg"):
        self.aiwg_dir = aiwg_dir
        self.state_truth = os.path.join(aiwg_dir, "state", "current_truth.json")
        self.receipts_file = os.path.join(aiwg_dir, "reports", "receipts.jsonl")

    def _get_git_head(self) -> str:
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        except Exception:
            return "UNKNOWN_COMMIT"

    def acquire_preflight_context(self) -> PreflightContext:
        git_head = self._get_git_head()
        current_pack = "NONE"
        certainty = 1.0
        is_frozen = True
        baseline = {}
        active_warnings = []

        if os.path.exists(self.state_truth):
            try:
                with open(self.state_truth, "r", encoding="utf-8") as f:
                    data = json.load(f)
                current_pack = data.get("current_pack", "NONE")
                certainty = data.get("certainty_score", 1.0)
                is_frozen = (current_pack == "NONE")
                baseline = data.get("metrics_baseline", {})
                active_warnings = data.get("active_warnings", [])
            except Exception:
                pass

        return PreflightContext(
            head_commit=git_head,
            current_pack=current_pack,
            certainty_score=certainty,
            is_frozen=is_frozen,
            metrics_baseline=baseline,
            active_warnings=active_warnings
        )

    def commit_execution_receipt(self, receipt: ExecutionReceipt) -> None:
        os.makedirs(os.path.dirname(self.receipts_file), exist_ok=True)
        data = {
            "receipt_id": receipt.receipt_id,
            "command_executed": receipt.command_executed,
            "exit_code": receipt.exit_code,
            "started_at": receipt.started_at.isoformat(),
            "finished_at": receipt.finished_at.isoformat(),
            "duration_seconds": receipt.duration_seconds,
            "causal_witness_hash": receipt.causal_witness_hash,
            "state_mutated": receipt.state_mutated
        }
        with open(self.receipts_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

    def run_postflight_audit(self, receipt: ExecutionReceipt) -> PostflightMetrics:
        # Improved post-flight validation with dynamic telemetry estimation
        status = "PASSED" if receipt.exit_code == 0 else "FAILED"
        
        # Estimate tokens based on command length and execution success
        # This will be replaced by a real Tokenizer in Pack 5.1
        base_cost = 10
        payload_cost = len(receipt.command_executed) // 10
        total_estimate = base_cost + payload_cost if receipt.exit_code == 0 else 5
        
        return PostflightMetrics(
            tokens_consumed=total_estimate,
            elapsed_ms=int(receipt.duration_seconds * 1000),
            validation_status=status,
            artifacts_generated=[self.receipts_file]
        )
