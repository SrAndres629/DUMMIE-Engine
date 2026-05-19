import os
import json
from pathlib import Path
from dummie.paths import ROOT, AIWG

class DummieConfig:
    def __init__(self):
        self.root_dir = ROOT
        self.aiwg_dir = AIWG
        self.env = self._load_env()
        self.identity = self._load_identity()
        self.truth = self._load_truth()

    def _load_env(self) -> dict:
        env_file = ROOT / ".env"
        data = {}
        if env_file.exists():
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            data[k.strip()] = v.strip().strip('"').strip("'")
            except Exception:
                pass
        return data

    def _load_identity(self) -> dict:
        identity_file = AIWG / "identity.json"
        if identity_file.exists():
            try:
                with open(identity_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _load_truth(self) -> dict:
        truth_file = AIWG / "state" / "current_truth.json"
        if truth_file.exists():
            try:
                with open(truth_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get(self, key: str, default=None):
        return self.env.get(key, os.environ.get(key, default))
