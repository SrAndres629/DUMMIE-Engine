# Spec: 166_l2_brain_organ_migration_contract
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

# Canonical organ directories (PACK R4)
_canonical_organs = {
    "context", "memory", "model_mesh", "cognition", "metacognition",
    "mission", "strategic", "daemon", "heartbeat", "governance",
    "infrastructure", "domain", "sdk", "proto", "structural_hardening"
}

_canonical_root_modules = {
    "action_graph", "token_cost_ledger", "neuron_ledger",
    "model_router", "model_discovery", "model_executor",
    "supervisor_protocol", "models", "embedding_mesh",
    "metagateway_adapter", "metagateway_policy",
    "metagateway_runtime_meter", "safe_fallbacks",
    "sensor_first_guard"
}

__all__ = ["DummieDaemon", "GatewayRequest", "SkillBinder", "AuthorityLevel", "MemoryNode4D"]

def __getattr__(name):
    """
    [CANONICAL] Resolución estática de atributos para L2 Brain.
    Elimina el redirector dinámico sys.meta_path en favor de una resolución explícita.
    """
    # Handle explicit class backward-compatibility imports
    if name == "DummieDaemon":
        try:
            from layers.l2_brain.daemon.daemon import DummieDaemon
            return DummieDaemon
        except (ModuleNotFoundError, ImportError):
            from layers.l2_brain.flat_brain.daemon import DummieDaemon
            return DummieDaemon

    if name == "GatewayRequest":
        try:
            from layers.l2_brain.infrastructure.gateway_contract import GatewayRequest
            return GatewayRequest
        except (ModuleNotFoundError, ImportError):
            from layers.l2_brain.flat_brain.gateway_contract import GatewayRequest
            return GatewayRequest

    if name == "SkillBinder":
        # SkillBinder is currently in layers/l2_brain/skill_binder.py (root of L2)
        # or in flat_brain
        try:
            from layers.l2_brain.skill_binder import SkillBinder
            return SkillBinder
        except (ModuleNotFoundError, ImportError):
            from layers.l2_brain.flat_brain.skill_binder import SkillBinder
            return SkillBinder

    if name == "AuthorityLevel":
        from layers.l2_brain.domain.authority import AuthorityLevel
        return AuthorityLevel

    if name == "MemoryNode4D":
        from layers.l2_brain.memory.models import MemoryNode4D
        return MemoryNode4D

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
