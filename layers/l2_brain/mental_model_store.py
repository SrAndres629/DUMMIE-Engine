
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
        data = model.to_dict() if hasattr(model, "to_dict") else asdict(model)
        with self.jsonl_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
        
        index = {}
        if self.index_path.exists():
            try: index = json.loads(self.index_path.read_text())
            except: pass
        index[model.model_id] = str(self.jsonl_path.relative_to(self.root.parent.parent))
        self.index_path.write_text(json.dumps(index, indent=2))
