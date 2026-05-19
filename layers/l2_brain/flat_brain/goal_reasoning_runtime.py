import re
from layers.l2_brain.business_goal_model import GoalClassification

class GoalReasoningRuntime:
    def __init__(self):
        pass

    def classify_goal(self, text: str) -> GoalClassification:
        text_lower = text.lower()
        
        # Check for revenue indicators
        revenue_keywords = ["facturar", "mrr", "usd", "dolares", "dólares", "pesos", "ventas", "revenue", "mensuales", "mensual", "ingresos"]
        technical_keywords = ["refactor", "tests", "código", "codigo", "git", "db", "database", "kuzu", "pipeline", "ci", "sdk", "cli", "python", "go"]
        ops_keywords = ["operaciones", "procesos", "automatizar", "flujo", "logística", "equipo", "infraestructura"]
        strategy_keywords = ["estrategia", "socio", "mentor", "plan", "largo plazo", "misión", "vision"]

        if any(kw in text_lower for kw in revenue_keywords):
            return GoalClassification(
                goal_type="revenue",
                confidence=0.95,
                description="Objetivo de crecimiento de ingresos o facturación mensual detectado."
            )
        elif any(kw in text_lower for kw in technical_keywords):
            return GoalClassification(
                goal_type="technical",
                confidence=0.90,
                description="Objetivo técnico de desarrollo, refactorización o infraestructura de software."
            )
        elif any(kw in text_lower for kw in ops_keywords):
            return GoalClassification(
                goal_type="operations",
                confidence=0.85,
                description="Objetivo operacional para automatizar o mejorar procesos internos."
            )
        elif any(kw in text_lower for kw in strategy_keywords):
            return GoalClassification(
                goal_type="strategy",
                confidence=0.80,
                description="Objetivo de estrategia de negocio o evolución a largo plazo."
            )
        else:
            return GoalClassification(
                goal_type="unknown",
                confidence=0.50,
                description="No se pudo determinar el tipo de objetivo con alta confianza."
            )

    def extract_target_mrr(self, text: str) -> float:
        # Look for numbers near dollar/usd symbols or MRR
        text_clean = text.lower().replace(",", "")
        # Match numbers like 10000, 10,000, 10k (convert 10k to 10000)
        # Regex to find numbers: matches digits optionally followed by 'k'
        match = re.search(r'(\d+)\s*(k|usd|mrr|dolares|dólares)?', text_clean)
        if match:
            val = float(match.group(1))
            suffix = match.group(2)
            if suffix == 'k':
                val *= 1000
            return val
        
        # Fallback default target if none found but it is a revenue goal
        return 10000.0
