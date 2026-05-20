import os
import sys
import importlib
import importlib.abc
import importlib.util

_base_dir = os.path.dirname(os.path.abspath(__file__))
_flat_dir = os.path.join(_base_dir, "flat_brain")

sys.path.insert(0, _flat_dir)
if _base_dir not in sys.path:
    sys.path.append(_base_dir)
_src_dir = os.path.join(_base_dir, "src")
if _src_dir not in sys.path:
    sys.path.append(_src_dir)

_flat_dir_list = os.listdir(_flat_dir) if os.path.isdir(_flat_dir) else []
_flat_modules = {
    f.replace('.py', '') for f in _flat_dir_list
    if f.endswith('.py') and not f.startswith('_') and os.path.isfile(os.path.join(_flat_dir, f))
}

_flat_subdirs = {
    d for d in _flat_dir_list
    if os.path.isdir(os.path.join(_flat_dir, d))
    and os.path.isfile(os.path.join(_flat_dir, d, '__init__.py'))
}

_flat_dotted_modules = {}
for _subdir in _flat_subdirs:
    _subpath = os.path.join(_flat_dir, _subdir)
    for _f in os.listdir(_subpath):
        if _f.endswith('.py') and not _f.startswith('_'):
            _modname = f"{_subdir}.{_f.replace('.py', '')}"
            _flat_dotted_modules[_modname] = os.path.join(_subpath, _f)

_canonical_organs = {
    "context", "memory", "model_mesh", "cognition", "metacognition",
    "mission", "strategic", "daemon", "heartbeat", "governance",
    "infrastructure", "domain", "sdk", "proto", "structural_hardening",
    "embedding_mesh",
}

_canonical_root_modules = {
    "action_graph", "token_cost_ledger", "neuron_ledger",
    "model_router", "model_discovery", "model_executor",
    "supervisor_protocol", "models", "embedding_mesh",
    "metagateway_adapter", "metagateway_policy",
    "metagateway_runtime_meter", "safe_fallbacks",
    "sensor_first_guard",
}

__all__ = ["DummieDaemon", "GatewayRequest", "SkillBinder", "AuthorityLevel", "MemoryNode4D"]


class _FlatBrainFallbackFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith('layers.l2_brain.'):
            return None
        subname = fullname[len('layers.l2_brain.'):]

        if not subname:
            return None
        if '.' in subname:
            if subname in _flat_dotted_modules:
                return importlib.util.spec_from_file_location(fullname, _flat_dotted_modules[subname])
            return None

        real_path = os.path.join(_base_dir, f"{subname}.py")
        real_dir = os.path.join(_base_dir, subname)
        if os.path.isfile(real_path) or os.path.isdir(real_dir):
            return None

        flat_file = os.path.join(_flat_dir, f"{subname}.py")
        if subname in _flat_modules and os.path.isfile(flat_file):
            return importlib.util.spec_from_file_location(fullname, flat_file)

        if subname in _flat_subdirs:
            flat_sub = os.path.join(_flat_dir, subname)
            if os.path.isdir(flat_sub):
                return importlib.util.spec_from_file_location(fullname, os.path.join(flat_sub, '__init__.py'))

        return None


sys.meta_path.insert(0, _FlatBrainFallbackFinder())


def __getattr__(name):
    if name == "DummieDaemon":
        try:
            from layers.l2_brain.daemon.daemon import DummieDaemon as _d
            return _d
        except (ModuleNotFoundError, ImportError):
            from layers.l2_brain.flat_brain.daemon import DummieDaemon as _d
            return _d

    if name == "GatewayRequest":
        try:
            from layers.l2_brain.infrastructure.gateway_contract import GatewayRequest as _g
            return _g
        except (ModuleNotFoundError, ImportError):
            from layers.l2_brain.flat_brain.gateway_contract import GatewayRequest as _g
            return _g

    if name == "SkillBinder":
        try:
            from layers.l2_brain.skill_binder import SkillBinder as _s
            return _s
        except (ModuleNotFoundError, ImportError):
            from layers.l2_brain.flat_brain.skill_binder import SkillBinder as _s
            return _s

    if name == "AuthorityLevel":
        from layers.l2_brain.domain.authority import AuthorityLevel as _a
        return _a

    if name == "MemoryNode4D":
        from layers.l2_brain.memory.models import MemoryNode4D as _m
        return _m

    if name in _canonical_organs:
        try:
            return importlib.import_module(f"layers.l2_brain.{name}")
        except ModuleNotFoundError:
            pass

    for organ in _canonical_organs:
        organ_dir = os.path.join(_base_dir, organ)
        if os.path.isdir(organ_dir):
            maybe_file = os.path.join(organ_dir, f"{name}.py")
            maybe_dir = os.path.join(organ_dir, name)
            if os.path.isfile(maybe_file) or os.path.isdir(maybe_dir):
                try:
                    return importlib.import_module(f"layers.l2_brain.{organ}.{name}")
                except ModuleNotFoundError:
                    pass

    try:
        return importlib.import_module(f"layers.l2_brain.flat_brain.{name}")
    except ModuleNotFoundError:
        pass

    raise AttributeError(f"module {__name__} has no attribute {name}")
