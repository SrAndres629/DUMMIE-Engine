import os
import sys
import importlib

_base_dir = os.path.dirname(os.path.abspath(__file__))

_src_dir = os.path.join(_base_dir, "src")
if _src_dir not in sys.path:
    sys.path.append(_src_dir)
if _base_dir not in sys.path:
    sys.path.append(_base_dir)

__all__ = [
    "DummieDaemon",
    "GatewayRequest",
    "SkillBinder",
    "AuthorityLevel",
    "MemoryNode4D",
]


def __getattr__(name):
    if name == "DummieDaemon":
        from layers.l2_brain.daemon.daemon import DummieDaemon as _d

        return _d

    if name == "GatewayRequest":
        from layers.l2_brain.infrastructure.gateway_contract import GatewayRequest as _g

        return _g

    if name == "SkillBinder":
        from layers.l2_brain.skill_binder import SkillBinder as _s

        return _s

    if name == "AuthorityLevel":
        from layers.l2_brain.domain.authority import AuthorityLevel as _a

        return _a

    if name == "MemoryNode4D":
        from layers.l2_brain.memory.models import MemoryNode4D as _m

        return _m

    raise AttributeError(f"module {__name__} has no attribute {name}")
