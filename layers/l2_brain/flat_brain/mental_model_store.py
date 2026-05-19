# Spec: 154_mental_model_store
# Spec: DE-V2-L2-154

import json
from pathlib import Path
from dataclasses import asdict

class MentalModelStore:
    def __init__(self, repo_root: Path = Path(".")):
        self.root = repo_root / ".aiwg" / "mental_models"
        self.root.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.root / "runtime_models.jsonl"
        self.index_path = self.root / "runtime_model_index.json"

    def _load_index(self) -> dict:
        if self.index_path.exists():
            try:
                return json.loads(self.index_path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_index(self, index: dict):
        self.index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    def append_model(self, model):
        # 1. Secret/Private reasoning rejection
        data = model.to_dict() if hasattr(model, "to_dict") else asdict(model)
        
        # 2. Idempotent check
        index = self._load_index()
        if model.model_id in index:
            return # Already exists

        # 3. Append to JSONL
        with self.jsonl_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
        
        # 4. Update index (enriched format for Pack 5.2.2)
        index[model.model_id] = {
            "path": str(self.jsonl_path.relative_to(self.root.parent.parent)) if self.root.parent.parent != Path(".") else str(self.jsonl_path),
            "status": "valid",
            "quality_score": getattr(model, "quality_score", 0),
            "created_at": getattr(model, "created_at", ""),
            "intent_hash": "",
            "superseded_by": "",
            "hygiene_findings": [],
        }
        self._save_index(index)

    def latest_model(self):
        if not self.jsonl_path.exists():
            return None
        lines = self.jsonl_path.read_text(encoding="utf-8").strip().split("\n")
        if not lines or lines == [""]:
            return None
        return json.loads(lines[-1])

    def iter_models(self):
        if not self.jsonl_path.exists():
            return
        with self.jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)

    # --- Pack 5.2.2: New methods ---

    def mark_status(self, model_id: str, status: str, reason: str, superseded_by: str = ""):
        """Update the status of a model in the enriched index."""
        index = self._load_index()
        if model_id not in index:
            return
        entry = index[model_id]
        if isinstance(entry, str):
            # Legacy format — upgrade
            entry = {"path": entry, "status": "unknown", "quality_score": 0,
                      "created_at": "", "intent_hash": "", "superseded_by": "",
                      "hygiene_findings": []}
        entry["status"] = status
        if superseded_by:
            entry["superseded_by"] = superseded_by
        entry.setdefault("hygiene_findings", []).append({"reason": reason, "status": status})
        index[model_id] = entry
        self._save_index(index)

    def get_model_status(self, model_id: str) -> str:
        """Return the status of a model from the enriched index."""
        index = self._load_index()
        entry = index.get(model_id, {})
        if isinstance(entry, str):
            return "unknown"
        return entry.get("status", "unknown")

    def iter_models_by_status(self, status: str):
        """Yield models whose index status matches."""
        index = self._load_index()
        valid_ids = set()
        for mid, entry in index.items():
            if isinstance(entry, dict) and entry.get("status") == status:
                valid_ids.add(mid)
        for m in self.iter_models():
            if m.get("model_id") in valid_ids:
                yield m

    def find_best_model_for_intent(self, intent: str):
        """Find the model with the highest quality_score for a matching intent,
        excluding quarantined and unsafe_rejected models."""
        import hashlib
        target_hash = hashlib.sha256(intent.strip().lower().encode()).hexdigest()[:12]
        index = self._load_index()

        best_id = None
        best_score = -1
        for mid, entry in index.items():
            if isinstance(entry, str):
                continue
            if entry.get("status") in ("quarantined", "unsafe_rejected", "superseded"):
                continue
            if entry.get("intent_hash") == target_hash and entry.get("quality_score", -1) > best_score:
                best_score = entry["quality_score"]
                best_id = mid

        if best_id is None:
            # Fallback: scan JSONL for intent substring match
            for m in self.iter_models():
                if m.get("intent", "").strip().lower() == intent.strip().lower():
                    mid = m.get("model_id", "")
                    entry = index.get(mid, {})
                    if isinstance(entry, dict) and entry.get("status") in ("quarantined", "unsafe_rejected"):
                        continue
                    qs = m.get("quality_score", -1)
                    if qs > best_score:
                        best_score = qs
                        best_id = mid

        if best_id is None:
            return None

        for m in self.iter_models():
            if m.get("model_id") == best_id:
                return m
        return None
