import warnings

warnings.warn(
    "layers.l2_brain.memory.kuzu_adapter is deprecated. "
    "Use layers.l2_brain.infrastructure.kuzu.KuzuRepository instead.",
    DeprecationWarning,
    stacklevel=2,
)

from layers.l2_brain.infrastructure.kuzu import KuzuRepository

__all__ = ["KuzuRepository"]
