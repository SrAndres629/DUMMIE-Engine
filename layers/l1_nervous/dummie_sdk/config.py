import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

CONFIG_PATH = Path(__file__).parents[1] / "configs" / "models_config.json"


@dataclass
class ModelSpec:
    model_id: str
    model_type: str
    provider: str
    priority: str = "MEDIUM"
    dimensions: Optional[int] = None
    context_length: Optional[int] = None


@dataclass
class AdapterRoute:
    provider: str
    module_path: str
    class_name: str


@dataclass
class SDKConfig:
    defaults: dict = field(default_factory=dict)
    models: list[ModelSpec] = field(default_factory=list)
    adapter_routes: list[AdapterRoute] = field(default_factory=list)
    lifecycle_ttl: dict = field(default_factory=dict)
    vram_threshold_mb: int = 2048
    ollama_host: str = "http://localhost:11434"

    def default_model(self, model_type: str) -> Optional[str]:
        return self.defaults.get(model_type)

    def get_model(self, model_id: str) -> Optional[ModelSpec]:
        for m in self.models:
            if m.model_id == model_id:
                return m
        return None

    def get_models_by_type(self, model_type: str) -> list[ModelSpec]:
        return [m for m in self.models if m.model_type == model_type]


def load_config(path: Optional[Path] = None) -> SDKConfig:
    p = path or CONFIG_PATH
    with open(p) as f:
        raw = json.load(f)

    cfg = SDKConfig(
        defaults=raw.get("defaults", {}),
        lifecycle_ttl=raw.get("lifecycle", {}).get("ttl_seconds", {}),
        vram_threshold_mb=raw.get("lifecycle", {}).get("vram_threshold_mb", 2048),
    )

    ollama_host = raw.get("providers", {}).get("ollama", {}).get("host", "http://localhost:11434")
    cfg.ollama_host = ollama_host

    for provider_name, provider_cfg in raw.get("providers", {}).items():
        for model_id, model_cfg in provider_cfg.get("models", {}).items():
            cfg.models.append(ModelSpec(
                model_id=model_id,
                model_type=model_cfg.get("type", ""),
                provider=model_cfg.get("provider", provider_name),
                priority=model_cfg.get("priority", "MEDIUM"),
                dimensions=model_cfg.get("dimensions"),
                context_length=model_cfg.get("context_length"),
            ))

    for provider_name, module_path in raw.get("adapter_map", {}).items():
        parts = module_path.rsplit(".", 1)
        cfg.adapter_routes.append(AdapterRoute(
            provider=provider_name,
            module_path=parts[0],
            class_name=parts[1],
        ))

    return cfg


_INSTANCE: Optional[SDKConfig] = None


def get_config(reload: bool = False) -> SDKConfig:
    global _INSTANCE
    if _INSTANCE is None or reload:
        _INSTANCE = load_config()
    return _INSTANCE
