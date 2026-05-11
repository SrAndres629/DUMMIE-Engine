import os
import json
import logging
import fcntl
from typing import Dict, Any, List, Optional

try:
    from infrastructure.adapters import (
        KuzuRepository, KuzuSkillRepository,
        DecisionLedgerAdapter, SessionLedgerAdapter,
        UnsafeBypassShieldAdapter, NativeShieldAdapter,
        SocraticodeAdapter, PhoenixAdapter
    )
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from infrastructure.adapters import (
        KuzuRepository, KuzuSkillRepository,
        DecisionLedgerAdapter, SessionLedgerAdapter,
        UnsafeBypassShieldAdapter, NativeShieldAdapter,
        SocraticodeAdapter, PhoenixAdapter
    )

logger = logging.getLogger("brain.adapters")

# [BRIDGE] Compatibility layer for hexagonal adapters.
# This file serves as a bridge to the new infrastructure/adapters/ structure.
# Direct imports from infrastructure.adapters are preferred.

__all__ = [
    "KuzuRepository", "KuzuSkillRepository",
    "DecisionLedgerAdapter", "SessionLedgerAdapter",
    "NativeShieldAdapter", "SocraticodeAdapter", "PhoenixAdapter"
]
