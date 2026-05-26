import warnings

warnings.warn(
    "layers.l2_brain.infrastructure.adapters.kuzu_repository is deprecated. "
    "Use layers.l2_brain.infrastructure.kuzu.KuzuRepository instead.",
    DeprecationWarning,
    stacklevel=2,
)

from layers.l2_brain.infrastructure.kuzu import KuzuRepository, KuzuSkillRepository

__all__ = ["KuzuRepository", "KuzuSkillRepository"]
