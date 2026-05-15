import logging
import os
import sys

# [HEXAGONAL BRIDGE] DE-V2-CROSS-51: Redirección al Dominio Soberano (L2)
# L1 actúa como puerto/adaptador, pero el modelo de información es soberano en L2.

try:
    from layers.l2_brain.models import SixDimensionalContext, AuthorityLevel, IntentType, AgentIntent
except ImportError:
    # Fallback si el repo root no está en el path. Mantiene import package-qualified
    # para no cargar layers/l2_brain/models.py como módulo top-level duplicado.
    root_dir = os.environ.get("DUMMIE_ROOT", os.environ.get("DUMMIE_ROOT_DIR", ""))
    if root_dir and root_dir not in sys.path:
        sys.path.append(root_dir)
    from layers.l2_brain.models import SixDimensionalContext, AuthorityLevel, IntentType, AgentIntent

# Re-exportamos para que el resto de L1 use 'domain.models'
__all__ = ["SixDimensionalContext", "AuthorityLevel", "IntentType", "AgentIntent"]
