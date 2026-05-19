import os
import sys
import importlib

# Add paths to sys.path to guarantee backward-compatibility for flat file resolution
_base_dir = os.path.dirname(os.path.abspath(__file__))
_flat_dir = os.path.join(_base_dir, "flat_brain")
if _flat_dir not in sys.path:
    sys.path.insert(0, _flat_dir)
if _base_dir not in sys.path:
    sys.path.append(_base_dir)
_src_dir = os.path.join(_base_dir, "src")
if _src_dir not in sys.path:
    sys.path.append(_src_dir)

# Redirect module imports from layers.l2_brain.xxx to layers.l2_brain.flat_brain.xxx
class FlatBrainRedirector:
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith("layers.l2_brain."):
            parts = fullname.split(".")
            if len(parts) > 2 and parts[2] not in {"src", "flat_brain", "tests"}:
                target_fullname = "layers.l2_brain.flat_brain." + ".".join(parts[2:])
                try:
                    mod = importlib.import_module(target_fullname)
                    sys.modules[fullname] = mod
                    parent_name = ".".join(parts[:-1])
                    if parent_name in sys.modules:
                        setattr(sys.modules[parent_name], parts[-1], mod)
                    return mod.__spec__
                except Exception:
                    pass
        return None

sys.meta_path.insert(0, FlatBrainRedirector())

__all__ = ["DummieDaemon", "GatewayRequest", "SkillBinder"]

def __getattr__(name):
    if name == "DummieDaemon":
        mod = importlib.import_module("layers.l2_brain.flat_brain.daemon")
        return getattr(mod, "DummieDaemon")
    if name == "GatewayRequest":
        mod = importlib.import_module("layers.l2_brain.flat_brain.gateway_contract")
        return getattr(mod, "GatewayRequest")
    if name == "SkillBinder":
        mod = importlib.import_module("layers.l2_brain.flat_brain.skill_binder")
        return getattr(mod, "SkillBinder")
    try:
        return importlib.import_module(f"layers.l2_brain.flat_brain.{name}")
    except ModuleNotFoundError:
        pass
    raise AttributeError(f"module {__name__} has no attribute {name}")
