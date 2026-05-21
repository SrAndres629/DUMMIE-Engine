from abc import ABC, abstractmethod
from brain.domain.context.capsule_models import ContextCapsule, TokenEconomyPolicy

class ContextCapsulePort(ABC):
    @abstractmethod
    def index_source_ast(self, file_paths: list) -> list:
        """Analiza sintácticamente los archivos y extrae nodos AST."""
        pass

    @abstractmethod
    def package_capsule(self, target_pack: str, policy: TokenEconomyPolicy) -> ContextCapsule:
        """Construye y comprime la cápsula contextual quirúrgica."""
        pass
