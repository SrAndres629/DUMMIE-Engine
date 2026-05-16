
import json
from pathlib import Path
from dataclasses import asdict

class MentalModelStore:
    def __init__(self, repo_root: Path = Path(".")):
        self.root = repo_root / ".aiwg" / "mental_models"
        self.root.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.root / "runtime_models.jsonl"
        self.index_path = self.root / "runtime_model_index.json"

    def append_model(self, model):
        # 1. Secret/Private reasoning rejection
        data = model.to_dict() if hasattr(model, "to_dict") else asdict(model)
        
        # 2. Idempotent check
        if self.index_path.exists():
            try:
                index = json.loads(self.index_path.read_text())
                if model.model_id in index:
                    return # Already exists
            except:
                pass

        # 3. Append to JSONL
        with self.jsonl_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
        
        # 4. Update index
        index = {}
        if self.index_path.exists():
            try:
                index = json.loads(self.index_path.read_text())
            except:
                pass
        index[model.model_id] = str(self.jsonl_path.relative_to(self.root.parent.parent))
        self.index_path.write_text(json.dumps(index, indent=2))

    def latest_model(self):
        if not self.jsonl_path.exists():
            return None
        lines = self.jsonl_path.read_text().strip().split("\n")
        if not lines:
            return None
        return json.loads(lines[-1])

    def iter_models(self):
        if not self.jsonl_path.exists():
            return
        with self.jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                yield json.loads(line)
