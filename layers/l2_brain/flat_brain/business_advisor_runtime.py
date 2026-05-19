import yaml
from pathlib import Path
from layers.l2_brain.business_goal_model import BusinessIntake

class BusinessAdvisorRuntime:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.policy_path = self.aiwg_root / "identity" / "business_growth_policy.yaml"
        self._policy = self._load_policy()

    def _load_policy(self) -> dict:
        if not self.policy_path.exists():
            return {
                "policy": {
                    "focus": "Crecimiento de negocios",
                    "metrics": ["MRR", "LTV/CAC", "AOV"]
                }
            }
        try:
            with open(self.policy_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def generate_advice(self, intake: BusinessIntake) -> dict:
        target = intake.target_mrr
        
        # Determine average order value (AOV) pricing tiers
        if target >= 50000:
            suggested_ticket = 5000.0
            tier = "Enterprise / B2B High-Ticket"
        elif target >= 10000:
            suggested_ticket = 2000.0
            tier = "Mid-Market / Agency High-Ticket"
        else:
            suggested_ticket = 500.0
            tier = "Low-Mid Tier / Productized Service"

        sales_needed = int(target / suggested_ticket)
        if sales_needed == 0:
            sales_needed = 1

        advice = {
            "tier_classification": tier,
            "suggested_ticket_price": suggested_ticket,
            "required_sales_monthly": sales_needed,
            "tactics": [
                f"Para alcanzar {target} USD/mes, se recomienda empaquetar una oferta '{tier}' con ticket promedio de {suggested_ticket} USD.",
                f"Esto reduce la presión operacional requiriendo solo {sales_needed} ventas/clientes nuevos al mes.",
                "Estructurar un embudo de prospección directa (Outbound) o llamada de consultoría para validar rápido.",
                "Mantener el costo de adquisición (CAC) por debajo del 30% del valor del ticket para asegurar flujo de caja sano."
            ],
            "risk_analysis": [
                "Depender de un solo canal de adquisición orgánico puede limitar la escalabilidad.",
                "La entrega del servicio debe estar semi-automatizada o productizada para evitar cuellos de botella de tiempo de entrega."
            ]
        }
        return advice
