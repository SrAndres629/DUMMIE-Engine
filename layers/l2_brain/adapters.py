import os
import logging
from typing import Dict, Any, List, Optional

try:
    from infrastructure.adapters import (
        KuzuRepository, KuzuSkillRepository,
        DecisionLedgerAdapter, SessionLedgerAdapter,
        NativeShieldAdapter, UnsafeBypassShieldAdapter,
        SocraticodeAdapter, PhoenixAdapter
    )
except ImportError:
    import sys
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(base_dir)
    sys.path.append(os.path.join(base_dir, "src"))
    from infrastructure.adapters import (
        KuzuRepository, KuzuSkillRepository,
        DecisionLedgerAdapter, SessionLedgerAdapter,
        NativeShieldAdapter, UnsafeBypassShieldAdapter,
        SocraticodeAdapter, PhoenixAdapter
    )

logger = logging.getLogger("brain.adapters")

# [BRIDGE] Compatibility layer for hexagonal adapters.
# This file serves as a bridge to the new infrastructure/adapters/ structure.
# Direct imports from infrastructure.adapters are preferred.

__all__ = [
    "KuzuRepository", "KuzuSkillRepository",
    "DecisionLedgerAdapter", "SessionLedgerAdapter",
    "NativeShieldAdapter", "UnsafeBypassShieldAdapter", "SocraticodeAdapter", "PhoenixAdapter"
]
