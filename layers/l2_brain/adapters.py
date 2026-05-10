import logging

try:
    from infrastructure.adapters.kuzu import KuzuRepository, KuzuSkillRepository
    from infrastructure.adapters.ledger import DecisionLedgerAdapter, SessionLedgerAdapter
    from infrastructure.adapters.external import NativeShieldAdapter, SocraticodeAdapter, PhoenixAdapter
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from infrastructure.adapters.kuzu import KuzuRepository, KuzuSkillRepository
    from infrastructure.adapters.ledger import DecisionLedgerAdapter, SessionLedgerAdapter
    from infrastructure.adapters.external import NativeShieldAdapter, SocraticodeAdapter, PhoenixAdapter

logger = logging.getLogger("brain.adapters")
