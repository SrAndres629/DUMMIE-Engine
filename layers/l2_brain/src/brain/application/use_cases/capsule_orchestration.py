from brain.application.ports.capsule_ports import ContextCapsulePort
from brain.domain.context.capsule_models import ContextCapsule, TokenEconomyPolicy

class CapsuleOrchestrationUseCase:
    def __init__(self, port: ContextCapsulePort):
        self.port = port

    def compile_capsule(self, target_pack: str, file_paths: list, policy: TokenEconomyPolicy) -> ContextCapsule:
        # 1. Index source code AST nodes
        ast_nodes = self.port.index_source_ast(file_paths)
        
        # 2. Package capsule using the infrastructure port
        capsule = self.port.package_capsule(target_pack, policy)
        
        # Override node list with our parsed AST nodes
        capsule.ast_nodes = ast_nodes
        
        return capsule
