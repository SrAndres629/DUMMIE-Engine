import abc, time, json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ContextProfile:
    temporal: dict = field(default_factory=dict)
    spatial: dict = field(default_factory=dict)
    semantic: dict = field(default_factory=dict)
    relational: dict = field(default_factory=dict)
    episodic: dict = field(default_factory=dict)
    instrumental: dict = field(default_factory=dict)

    def to_prompt(self) -> str:
        parts = []
        for name, data in [
            ("Tiempo", self.temporal),
            ("Espacio", self.spatial),
            ("Semántica", self.semantic),
            ("Relaciones", self.relational),
            ("Memoria", self.episodic),
            ("Herramientas", self.instrumental),
        ]:
            if data:
                parts.append(f"[{name}]: {json.dumps(data, ensure_ascii=False)}")
        return "\n".join(parts)


class ContextDimension(abc.ABC):
    name: str

    @abc.abstractmethod
    async def collect(self) -> dict: ...


class ContextEngine:
    def __init__(self):
        self._dimensions: dict[str, ContextDimension] = {}

    def register(self, dimension: ContextDimension):
        self._dimensions[dimension.name] = dimension

    async def build_profile(self, active_dims: list[str] = None) -> ContextProfile:
        profile = ContextProfile()
        for name, dim in self._dimensions.items():
            if active_dims and name not in active_dims:
                continue
            data = await dim.collect()
            setattr(profile, name, data)
        return profile
