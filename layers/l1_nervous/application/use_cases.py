from ..domain.services import NervousDomainService

class BrainToolUseCases:
    def __init__(self, orchestrator, proxy_manager):
        self.orchestrator = orchestrator
        self.proxy_manager = proxy_manager
        self.domain_service = NervousDomainService(orchestrator)

    async def execute_crystallization(self, payload: str, context: dict) -> str:
        try:
            return await self.domain_service.crystallize_knowledge(payload, context)
        except PermissionError as e:
            return f"[L1-MCP] {str(e)}"
        except Exception as e:
            return f"[L1-MCP] UNEXPECTED_ERROR: {str(e)}"

    async def log_brain_lesson(self, issue: str, correction: str) -> str:
        try:
            return self.domain_service.record_lesson(issue, correction)
        except PermissionError as e:
            return f"[L1-MCP] {str(e)}"
        except Exception as e:
            return f"[L1-MCP] UNEXPECTED_ERROR: {str(e)}"

    async def ping_gateway(self) -> str:
        return f"[L1-MCP] Engine Alive. Clock: {self.orchestrator.lamport_clock}"
