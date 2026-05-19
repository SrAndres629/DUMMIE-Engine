class RevenueGoalPlanner:
    def __init__(self):
        pass

    def build_roadmap(self, target_mrr: float, goal_type: str) -> list[dict]:
        if goal_type == "revenue":
            return [
                {
                    "phase": "Fase 1: Diagnóstico y Modelado Económico",
                    "duration": "Días 1 a 7",
                    "actions": [
                        "Construir Revenue Intake y definir unit economics básicos.",
                        "Calcular cantidad de ventas necesarias según ticket promedio estimado.",
                        "Identificar cuellos de botella en el embudo actual."
                    ]
                },
                {
                    "phase": "Fase 2: Rediseño de Oferta y Empaquetamiento",
                    "duration": "Días 8 a 15",
                    "actions": [
                        "Realizar Offer Audit para estructurar una oferta de alto valor (High-Ticket).",
                        "Eliminar fricción de compra mediante garantías o bonos.",
                        "Validar la oferta preliminar con 3 prospectos cualificados."
                    ]
                },
                {
                    "phase": "Fase 3: Configuración de Canales de Adquisición",
                    "duration": "Días 16 a 25",
                    "actions": [
                        "Lanzar Acquisition Experiment Tracker con canales orgánicos (LinkedIn/Email outreach) y de pago.",
                        "Configurar Lead Pipeline Tracker con CRM Intake básico.",
                        "Iniciar secuencia de nutrición y prospección activa."
                    ]
                },
                {
                    "phase": "Fase 4: Ejecución Comercial y Cierre",
                    "duration": "Días 26 a 30",
                    "actions": [
                        "Agendar y ejecutar llamadas de venta/demostración estructuradas.",
                        "Revisar métricas clave en el Weekly Business Review Dashboard.",
                        "Ajustar precios según feedback directo del mercado."
                    ]
                }
            ]
        else:
            return [
                {
                    "phase": "Fase 1: Análisis de Requisitos y Alcance",
                    "duration": "Semana 1",
                    "actions": [
                        "Definir especificaciones técnicas y criterios de aceptación.",
                        "Censar dependencias e integraciones críticas en boundaries."
                    ]
                },
                {
                    "phase": "Fase 2: Desarrollo e Implementación Core",
                    "duration": "Semana 2",
                    "actions": [
                        "Codificar componentes puros del Dominio aplicando DDD.",
                        "Integrar infraestructura mediante adapters y puertos estables."
                    ]
                },
                {
                    "phase": "Fase 3: Pruebas y Hardening",
                    "duration": "Semana 3",
                    "actions": [
                        "Configurar andamiaje de tests unitarios y de integración.",
                        "Ejecutar verificaciones de seguridad y rendimiento."
                    ]
                },
                {
                    "phase": "Fase 4: Despliegue y Aceptación",
                    "duration": "Semana 4",
                    "actions": [
                        "Validar con el operador principal mediante receipts firmados.",
                        "Habilitar de forma continua en producción."
                    ]
                }
            ]
