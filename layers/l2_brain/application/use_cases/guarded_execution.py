from typing import Callable, Any
from brain.application.ports.kernel_ports import KernelOperatingBoundaryPort
from brain.domain.governance.kernel_contracts import ExecutionReceipt
from datetime import datetime, timezone
import uuid

class GuardedExecutionUseCase:
    def __init__(self, port: KernelOperatingBoundaryPort):
        self.port = port

    def execute_guarded(self, command_str: str, execution_fn: Callable[[], Any]) -> Any:
        # 1. Preflight check
        preflight = self.port.acquire_preflight_context()
        if preflight.is_frozen and preflight.current_pack == "NONE":
            # Kernel is frozen, verify that command is read-only or explicit override
            # We strictly prevent mutations:
            is_mutation = any(kw in command_str.lower() for kw in ["mutate", "write", "commit", "push", "delete", "remove"])
            if is_mutation:
                raise PermissionError("ERROR: Kernel is frozen. Mutation commands are gated.")

        started_at = datetime.now(timezone.utc)
        exit_code = 0
        try:
            result = execution_fn()
        except Exception as e:
            exit_code = 1
            raise e
        finally:
            finished_at = datetime.now(timezone.utc)
            duration = (finished_at - started_at).total_seconds()
            
            # Generate cryptographic receipt
            receipt = ExecutionReceipt(
                receipt_id=str(uuid.uuid4()),
                command_executed=command_str,
                exit_code=exit_code,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration,
                causal_witness_hash=preflight.head_commit, # Causal witness bindings
                state_mutated=(exit_code == 0)
            )
            self.port.commit_execution_receipt(receipt)
            self.port.run_postflight_audit(receipt)
            
        return result
