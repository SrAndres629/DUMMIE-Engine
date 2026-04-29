import json
import fcntl
from typing import Dict, Any

class DecisionLedgerAdapter:
    def __init__(self, ledger_path: str, lessons_path: str, ambiguities_path: str, ontological_map_path: str):
        self.ledger_path = ledger_path
        self.lessons_path = lessons_path
        self.ambiguities_path = ambiguities_path
        self.ontological_map_path = ontological_map_path

    def log_resolution(self, entry: Dict[str, Any]):
        with open(self.ledger_path, "a") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def log_lesson(self, entry: Dict[str, Any]):
        with open(self.lessons_path, "a") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def log_ambiguity(self, entry: Dict[str, Any]):
        with open(self.ambiguities_path, "a") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

class SessionLedgerAdapter:
    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
