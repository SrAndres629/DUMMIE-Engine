import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List

logger = logging.getLogger("brain.neuron_ledger")

@dataclass
class NeuronStats:
    model_id: str
    reputation: float = 100.0
    total_tasks: int = 0
    successes: int = 0
    failures: int = 0
    avg_latency: float = 0.0
    rewards: int = 0
    penalties: int = 0

class NeuronLedger:
    """
    [L2_BRAIN] Sistema de reputación social para neuronas.
    Permite al router elegir el mejor modelo basado en su historial real.
    """
    def __init__(self):
        self.neurons: Dict[str, NeuronStats] = {}

    def get_stats(self, model_id: str) -> NeuronStats:
        if model_id not in self.neurons:
            self.neurons[model_id] = NeuronStats(model_id=model_id)
        return self.neurons[model_id]

    def record_success(self, model_id: str, latency: float):
        stats = self.get_stats(model_id)
        stats.total_tasks += 1
        stats.successes += 1
        # Media móvil para latencia
        stats.avg_latency = (stats.avg_latency * (stats.successes - 1) + latency) / stats.successes
        stats.reputation = min(150.0, stats.reputation + 1.0)
        logger.info(f"NeuronLedger: Success for {model_id}. Reputation: {stats.reputation}")

    def record_failure(self, model_id: str, error: str):
        stats = self.get_stats(model_id)
        stats.total_tasks += 1
        stats.failures += 1
        stats.reputation = max(0.0, stats.reputation - 5.0)
        logger.warning(f"NeuronLedger: Failure for {model_id} ({error}). Reputation: {stats.reputation}")

    def reward(self, model_id: str, amount: float = 5.0):
        stats = self.get_stats(model_id)
        stats.rewards += 1
        stats.reputation = min(200.0, stats.reputation + amount)
        
    def penalize(self, model_id: str, amount: float = 10.0):
        stats = self.get_stats(model_id)
        stats.penalties += 1
        stats.reputation = max(0.0, stats.reputation - amount)
