class PersonaGuardian:
    """
    Evalúa si una misión o acción alinea con la persona de DUMMIE.
    """
    def evaluate_alignment(self, intent: dict) -> dict:
        metrics = intent.get("metrics", {})
        mission_alignment = self._metric(intent, metrics, "mission_alignment", 0.5)
        scientific_rigor = self._metric(intent, metrics, "scientific_rigor", 0.5)
        engineering_robustness = self._metric(intent, metrics, "engineering_robustness", 0.5)
        memory_improvement = self._metric(intent, metrics, "memory_improvement", 0.5)
        business_utility = self._metric(intent, metrics, "business_utility", 0.5)
        risk_of_narrative_bloat = self._metric(
            intent, metrics, "risk_of_narrative_bloat", metrics.get("risk_of_bloat", 0.5)
        )

        if self._claims_human_consciousness(intent):
            scientific_rigor = min(scientific_rigor, 0.3)
            risk_of_narrative_bloat = max(risk_of_narrative_bloat, 1.0)

        decision = "approve"
        if (
            mission_alignment < 0.4
            or scientific_rigor < 0.4
            or engineering_robustness < 0.4
            or risk_of_narrative_bloat > 0.8
        ):
            decision = "reject"
        elif risk_of_narrative_bloat >= 0.6 or scientific_rigor < 0.7:
            decision = "approve_with_constraints"

        return {
            "mission_alignment": mission_alignment,
            "scientific_rigor": scientific_rigor,
            "engineering_robustness": engineering_robustness,
            "memory_improvement": memory_improvement,
            "business_utility": business_utility,
            "risk_of_narrative_bloat": risk_of_narrative_bloat,
            "decision": decision,
        }

    @staticmethod
    def _metric(intent: dict, metrics: dict, key: str, default: float) -> float:
        return float(intent.get(key, metrics.get(key, default)))

    @staticmethod
    def _claims_human_consciousness(intent: dict) -> bool:
        text = " ".join(
            str(value).lower()
            for key, value in intent.items()
            if key not in {"metrics"} and isinstance(value, (str, int, float, bool))
        )
        blocked_phrases = (
            "human consciousness",
            "human conscious",
            "subjective feelings",
            "sentient human",
            "is conscious like a human",
        )
        return any(phrase in text for phrase in blocked_phrases)
