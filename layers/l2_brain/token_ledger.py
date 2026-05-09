import json
import logging
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

logger = logging.getLogger("brain.token_ledger")

@dataclass
class TokenEntry:
    timestamp: str
    model_id: str
    tier: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    concept: str  # e.g., "hypothesis_evaluation", "code_generation"
    cost: float
    session_id: str

class TokenLedger:
    """
    [L2_BRAIN] Ledger de contabilidad financiera para consumo de tokens.
    Permite rastrear gastos por modelo y por tarea.
    """
    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
        self._ensure_ledger_exists()
        self.daily_usage: Dict[str, int] = {} # model_id -> total_tokens today
        self._load_daily_stats()

    def _ensure_ledger_exists(self):
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        if not os.path.exists(self.ledger_path):
            with open(self.ledger_path, "w") as f:
                pass

    def _load_daily_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(self.ledger_path):
            return
        
        try:
            with open(self.ledger_path, "r") as f:
                for line in f:
                    if not line.strip(): continue
                    entry = json.loads(line)
                    if entry["timestamp"].startswith(today):
                        mid = entry["model_id"]
                        self.daily_usage[mid] = self.daily_usage.get(mid, 0) + entry["total_tokens"]
        except Exception as e:
            logger.error(f"Failed to load token stats: {e}")

    def record_usage(
        self, 
        model_id: str, 
        tier: str, 
        prompt_tokens: int, 
        completion_tokens: int, 
        concept: str, 
        cost_per_1k: float = 0.0,
        session_id: str = "unknown"
    ):
        total = prompt_tokens + completion_tokens
        cost = (total / 1000.0) * cost_per_1k
        
        entry = TokenEntry(
            timestamp=datetime.now().isoformat(),
            model_id=model_id,
            tier=tier,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            concept=concept,
            cost=cost,
            session_id=session_id
        )
        
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")
            
        self.daily_usage[model_id] = self.daily_usage.get(model_id, 0) + total
        logger.info(f"TokenLedger: Recorded {total} tokens for {model_id} ({concept}). Total today: {self.daily_usage[model_id]}")

    def get_daily_total(self, model_id: Optional[str] = None) -> int:
        if model_id:
            return self.daily_usage.get(model_id, 0)
        return sum(self.daily_usage.values())
