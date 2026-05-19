import yaml
from pathlib import Path

class CreatorContextRuntime:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.profile_path = self.aiwg_root / "identity" / "creator_profile.yaml"
        self._profile = self._load_profile()

    def _load_profile(self) -> dict:
        if not self.profile_path.exists():
            # Standard fallback
            return {
                "creator": {
                    "full_name": "Jorge Andrés Aguirre Cordero",
                    "preferred_name": "Jorge",
                    "role": "creator/principal_operator/strategic_owner"
                },
                "relationship": {
                    "dummie_role": ["mentor estratégico", "socio estratégico"]
                },
                "operating_preferences": {
                    "communication_style": ["directo", "estratégico"],
                    "default_behavior": ["no adular", "detectar objetivos reales"]
                }
            }
        
        try:
            with open(self.profile_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return data
        except Exception:
            return {}

    def get_creator_name(self) -> str:
        return self._profile.get("creator", {}).get("full_name", "Jorge Andrés Aguirre Cordero")

    def get_preferred_name(self) -> str:
        return self._profile.get("creator", {}).get("preferred_name", "Jorge")

    def get_creator_role(self) -> str:
        return self._profile.get("creator", {}).get("role", "creator/principal_operator/strategic_owner")

    def get_dummie_roles(self) -> list[str]:
        return self._profile.get("relationship", {}).get("dummie_role", [])

    def get_operating_preferences(self) -> dict:
        return self._profile.get("operating_preferences", {})
