from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Violation:
    file: str
    line: int
    severity: Severity
    rule: str
    message: str
    suggestion: str = ""

    @property
    def formatted(self) -> str:
        return f"  [{self.severity.value.upper()}] {self.file}:{self.line} — {self.message}"


@dataclass
class Rule:
    name: str
    description: str
    severity: Severity
    pattern: str = ""
    check_fn: Optional[callable] = None

    def check(self, file_path: str, content: str) -> list[Violation]:
        violations: list[Violation] = []
        if self.pattern:
            import re

            for i, line in enumerate(content.splitlines(), 1):
                if re.search(self.pattern, line):
                    violations.append(
                        Violation(
                            file=file_path,
                            line=i,
                            severity=self.severity,
                            rule=self.name,
                            message=self.description,
                        )
                    )
        if self.check_fn:
            result = self.check_fn(file_path, content)
            if result:
                violations.extend(result)
        return violations


HARDCODED_MODELS = Rule(
    name="hardcoded-model",
    description="Hardcoded model string — use SDK config instead",
    severity=Severity.ERROR,
    pattern=r'"(gemma3:1b|gemma4:e4b|BAAI/bge-small-en-v1\.5|cross-encoder/ms-marco-MiniLM-L-2-v2)"',
)

LEGACY_IMPORT = Rule(
    name="legacy-import",
    description="Import from legacy location instead of dummie_sdk",
    severity=Severity.WARNING,
    pattern=r"from (models|routing|embeddings)\.",
)

DUPLICATE_ENSURE_LOADED = Rule(
    name="duplicate-ensure-loaded",
    description="Duplicate _ensure_loaded pattern — use SDK base strategy",
    severity=Severity.WARNING,
    pattern=r"async def _ensure_loaded",
)

HARDCODED_DIMENSIONS = Rule(
    name="hardcoded-dimensions",
    description="Hardcoded embedding dimensions — derive from model config",
    severity=Severity.WARNING,
    pattern=r"self\._dimensions\s*=\s*384",
)

LEGACY_LOCAL_LLM = Rule(
    name="legacy-local-llm",
    description="Direct ollama.chat() call — use SDK OllamaAdapter instead",
    severity=Severity.ERROR,
    pattern=r"ollama\.(chat|async_chat|generate)\(",
)

LEGACY_EMBEDDING_SERVICE = Rule(
    name="legacy-embedding-service",
    description="Direct EmbeddingService usage — use SDK FastEmbedAdapter instead",
    severity=Severity.WARNING,
    pattern=r"from embeddings\.(embedding_service|embedding_router)",
)


def check_legacy_model_registry(file_path: str, content: str) -> list[Violation]:
    violations: list[Violation] = []
    if "models/model_registry.py" in file_path and "DEFAULT_CONFIG" in content:
        violations.append(
            Violation(
                file=file_path,
                line=1,
                severity=Severity.WARNING,
                rule="legacy-registry-config",
                message="DEFAULT_CONFIG in code — migrate to configs/models_config.json",
                suggestion="Move model config to configs/models_config.json and use SDKConfig.load_config()",
            )
        )
    return violations


LEGACY_REGISTRY_CONFIG = Rule(
    name="legacy-registry-config",
    description="Model config in Python code instead of SSOT JSON",
    severity=Severity.WARNING,
    check_fn=check_legacy_model_registry,
)


RULES: list[Rule] = [
    HARDCODED_MODELS,
    LEGACY_IMPORT,
    DUPLICATE_ENSURE_LOADED,
    HARDCODED_DIMENSIONS,
    LEGACY_LOCAL_LLM,
    LEGACY_EMBEDDING_SERVICE,
    LEGACY_REGISTRY_CONFIG,
]
