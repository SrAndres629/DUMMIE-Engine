import logging
import os
import sys

# [HEXAGONAL BRIDGE] Redirección al Dominio Soberano (L2)
# L1 actúa como puerto/adaptador, pero el modelo de información es soberano en L2.

try:
    from models import SixDimensionalContext, AuthorityLevel, IntentType, AgentIntent
except ImportError:
    # Fallback si no está en el path (aunque debería estar según mcp_config.json)
    sys.path.append(os.path.join(os.environ.get("DUMMIE_ROOT_DIR", ""), "layers/l2_brain"))
    from models import SixDimensionalContext, AuthorityLevel, IntentType, AgentIntent

# Re-exportamos para que el resto de L1 use 'domain.models'
__all__ = ["SixDimensionalContext", "AuthorityLevel", "IntentType", "AgentIntent"]
