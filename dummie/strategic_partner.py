from __future__ import annotations

from dummie.paths import AIWG
from layers.l2_brain.strategic_partner_runtime import StrategicPartnerRuntime


class DummieStrategicPartner:
    def __init__(self):
        self.runtime = StrategicPartnerRuntime(AIWG)

    def advise(self, goal_statement: str) -> dict:
        return self.runtime.advise(goal_statement)
