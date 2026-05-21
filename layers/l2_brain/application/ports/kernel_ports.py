from abc import ABC, abstractmethod
from brain.domain.governance.kernel_contracts import PreflightContext, ExecutionReceipt, PostflightMetrics

class KernelOperatingBoundaryPort(ABC):
    @abstractmethod
    def acquire_preflight_context(self) -> PreflightContext:
        """Adquiere y valida el estado físico antes de cualquier ejecución."""
        pass

    @abstractmethod
    def commit_execution_receipt(self, receipt: ExecutionReceipt) -> None:
        """Persiste de forma inmutable el recibo de ejecución."""
        pass

    @abstractmethod
    def run_postflight_audit(self, receipt: ExecutionReceipt) -> PostflightMetrics:
        """Ejecuta los linters de overclaim y validadores sobre el estado resultante."""
        pass
