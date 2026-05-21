# Spec Reference: 12_6d_context_model
import os
from enum import Enum
from typing import Optional


class ComponentType(Enum):
    INFRASTRUCTURE = "L0"
    ADAPTER = "L1"
    CORE = "L2"
    SHIELD = "L3"
    EXTENSION = "L4"
    MUSCLE = "L5"
    SOUL = "L6"
    SCRIPT = "SCRIPT"


class ExpansionPolicy:
    """
    [L2_BRAIN] Define la política soberana de organización de archivos.
    Asegura que DUMMIE no ensucie el repositorio al auto-programarse.
    """

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.mapping = {
            ComponentType.INFRASTRUCTURE: "infra",  # Or l0_overseer
            ComponentType.ADAPTER: "layers/l1_nervous/tools_impl",
            ComponentType.CORE: "layers/l2_brain",
            ComponentType.SHIELD: "layers/l3_shield",
            ComponentType.EXTENSION: "layers/l4_ext",
            ComponentType.MUSCLE: "layers/l5_muscle",
            ComponentType.SOUL: "layers/l6_soul",
            ComponentType.SCRIPT: "scripts",
        }

    def resolve_path(self, component_type: ComponentType, filename: str) -> str:
        sub_path = self.mapping.get(component_type, "layers/l4_ext")
        target_dir = os.path.join(self.root_dir, sub_path)
        os.makedirs(target_dir, exist_ok=True)
        return os.path.join(target_dir, filename)

    def categorize_mission(self, mission: str) -> ComponentType:
        mission = mission.lower()
        if any(word in mission for word in ["mcp", "adapter", "gateway", "connect"]):
            return ComponentType.ADAPTER
        if any(word in mission for word in ["policy", "guard", "security", "audit"]):
            return ComponentType.SHIELD
        if any(word in mission for word in ["model", "reason", "brain", "intent"]):
            return ComponentType.CORE
        if any(word in mission for word in ["script", "bash", "cli", "run"]):
            return ComponentType.SCRIPT
        if any(word in mission for word in ["personality", "alignment", "voice"]):
            return ComponentType.SOUL

        return ComponentType.EXTENSION
