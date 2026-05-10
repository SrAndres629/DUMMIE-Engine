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
