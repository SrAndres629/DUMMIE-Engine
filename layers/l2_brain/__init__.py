# Spec: 166_l2_brain_organ_migration_contract
import os
import sys
import importlib
from importlib.machinery import PathFinder

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

# Canonical organ directories (PACK R4)
_canonical_organs = {
    "context", "memory", "model_mesh", "cognition", "metacognition",
    "mission", "strategic", "daemon", "heartbeat", "governance",
    "infrastructure", "domain", "sdk", "proto", "structural_hardening"
}

_canonical_root_modules = {
    "action_graph", "token_cost_ledger", "neuron_ledger",
    "model_router", "model_discovery", "model_executor",
    "supervisor_protocol", "models"
}

# Redirect module imports from layers.l2_brain.xxx to canonical organs first,
# then fall back to layers.l2_brain.flat_brain.xxx
class L2BrainRedirector:
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith("layers.l2_brain."):
            parts = fullname.split(".")
            if len(parts) > 2 and parts[2] not in {"src", "flat_brain", "tests", "__pycache__"}:
                organ = parts[2]
                if organ in _canonical_root_modules:
                    return None
                
                # If we are importing a canonical organ, check if the module physically exists there.
                if organ in _canonical_organs:
                    subpath_parts = parts[3:]
                    if not subpath_parts:
                        return None
                    target_path = os.path.join(_base_dir, organ, *subpath_parts)
                    if os.path.isfile(target_path + ".py") or os.path.isdir(target_path):
                        return None


                # Otherwise, this is a top-level import like `layers.l2_brain.some_flat_module`.
                # We need to find if it was migrated to one of the canonical organs,
                # or if it's still in flat_brain.
                target_fullname = None
                module_name = parts[2]
                
                for canonical_organ in _canonical_organs:
                    organ_dir = os.path.join(_base_dir, canonical_organ)
                    if os.path.isfile(os.path.join(organ_dir, f"{module_name}.py")) or os.path.isdir(os.path.join(organ_dir, module_name)):
                        target_fullname = f"layers.l2_brain.{canonical_organ}." + ".".join(parts[2:])
                        break
                
                if not target_fullname:
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

sys.meta_path.insert(0, L2BrainRedirector())

__all__ = ["DummieDaemon", "GatewayRequest", "SkillBinder"]

def __getattr__(name):
    # Handle explicit class backward-compatibility imports
    if name == "DummieDaemon":
        try:
            mod = importlib.import_module("layers.l2_brain.daemon.daemon")
            return getattr(mod, "DummieDaemon")
        except (ModuleNotFoundError, AttributeError):
            mod = importlib.import_module("layers.l2_brain.flat_brain.daemon")
            return getattr(mod, "DummieDaemon")
    if name == "GatewayRequest":
        try:
            mod = importlib.import_module("layers.l2_brain.infrastructure.gateway_contract")
            return getattr(mod, "GatewayRequest")
        except (ModuleNotFoundError, AttributeError):
            mod = importlib.import_module("layers.l2_brain.flat_brain.gateway_contract")
            return getattr(mod, "GatewayRequest")
    if name == "SkillBinder":
        try:
            mod = importlib.import_module("layers.l2_brain.flat_brain.skill_binder")
            return getattr(mod, "SkillBinder")
        except (ModuleNotFoundError, AttributeError):
            pass

    # First try canonical organ
    if name in _canonical_organs:
        try:
            return importlib.import_module(f"layers.l2_brain.{name}")
        except ModuleNotFoundError:
            pass

    # Check if the name exists as a module under any canonical organ
    for organ in _canonical_organs:
        organ_dir = os.path.join(_base_dir, organ)
        if os.path.isdir(organ_dir):
            if os.path.isfile(os.path.join(organ_dir, f"{name}.py")) or os.path.isdir(os.path.join(organ_dir, name)):
                try:
                    return importlib.import_module(f"layers.l2_brain.{organ}.{name}")
                except ModuleNotFoundError:
                    pass

    # Fall back to flat_brain
    try:
        return importlib.import_module(f"layers.l2_brain.flat_brain.{name}")
    except ModuleNotFoundError:
        pass
    raise AttributeError(f"module {__name__} has no attribute {name}")
