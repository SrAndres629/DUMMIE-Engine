import os
import sys
# [TABULA RASA] Asegurar que el paquete 'brain' en src/ es descubrible.
_base_dir = os.path.dirname(os.path.abspath(__file__))
if _base_dir not in sys.path:
    sys.path.append(_base_dir)
_src_dir = os.path.join(_base_dir, "src")
if _src_dir not in sys.path:
    sys.path.append(_src_dir)

# [HARDENING] Lazy Loading de componentes pesados para evitar side-effects en imports de contratos.
__all__ = ["DummieDaemon", "GatewayRequest", "SkillBinder"]

def __getattr__(name):
    if name == "DummieDaemon":
        from .daemon import DummieDaemon
        return DummieDaemon
    if name == "GatewayRequest":
        from .gateway_contract import GatewayRequest
        return GatewayRequest
    if name == "SkillBinder":
        from .skill_binder import SkillBinder
        return SkillBinder
    raise AttributeError(f"module {__name__} has no attribute {name}")
