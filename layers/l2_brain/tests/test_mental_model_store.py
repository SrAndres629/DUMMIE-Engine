from mental_model_store import MentalModelStore
from mental_model_runtime import build_mental_model_for_intent
from pathlib import Path
import json
def test_store_append():
    store = MentalModelStore(Path("."))
    model = build_mental_model_for_intent("test")
    store.append_model(model)
    assert store.jsonl_path.exists()
    assert model.model_id in store.index_path.read_text()
