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
