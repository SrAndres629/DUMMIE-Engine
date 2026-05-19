from layers.l2_brain.business_goal_model import ToolOpportunity

class ToolOpportunityDetector:
    def __init__(self):
        pass

    def detect_opportunities(self, goal: str, goal_type: str) -> list[ToolOpportunity]:
        opportunities = []
        if goal_type == "revenue":
            opportunities.extend([
                ToolOpportunity(
                    name="revenue_calculator",
                    description="Calculadora interactiva para simular ticket promedio, tasa de conversión y leads necesarios para alcanzar la meta.",
                    opportunity_type="calculator"
                ),
                ToolOpportunity(
                    name="offer_audit_template",
                    description="Plantilla estructurada para auditar la propuesta de valor y empaquetamiento de ofertas de ticket alto.",
                    opportunity_type="template"
                ),
                ToolOpportunity(
                    name="crm_intake_sheet",
                    description="Hoja de cálculo simplificada para registrar leads y leads calificados en pipelines de ventas directas.",
                    opportunity_type="tracker"
                ),
                ToolOpportunity(
                    name="acquisition_experiment_tracker",
                    description="Matriz de priorización ICE para probar canales de adquisición orgánicos y de pago de forma metódica.",
                    opportunity_type="tracker"
                ),
                ToolOpportunity(
                    name="unit_economics_calculator",
                    description="Modelo financiero para determinar margen neto de producto, costo de entrega de servicio y CAC admisible.",
                    opportunity_type="calculator"
                )
            ])
        elif goal_type == "technical":
            opportunities.extend([
                ToolOpportunity(
                    name="testing_harness_generator",
                    description="Generador automático de andamiaje para tests unitarios y de integración mockeados.",
                    opportunity_type="generator"
                ),
                ToolOpportunity(
                    name="dependency_integrity_auditor",
                    description="Scanner estático de imports de paquetes y dependencias obsoletas en el entorno.",
                    opportunity_type="scanner"
                ),
                ToolOpportunity(
                    name="schema_contract_validator",
                    description="Parser JSON-schema para asegurar contratos estrictos de API en boundaries.",
                    opportunity_type="validator"
                )
            ])
        else:
            opportunities.extend([
                ToolOpportunity(
                    name="gantt_milestone_tracker",
                    description="Generador de diagramas de Gantt basados en texto para visualizar hitos e interdependencias.",
                    opportunity_type="tracker"
                ),
                ToolOpportunity(
                    name="daily_standup_summarizer",
                    description="Generador de minutas de reunión enfocado en blockers y next actions diarias.",
                    opportunity_type="summarizer"
                )
            ])
        return opportunities
