class StrategicQuestionGenerator:
    def __init__(self):
        pass

    def generate_questions(self, goal: str, goal_type: str) -> list[str]:
        if goal_type == "revenue":
            return [
                "¿Qué producto o servicio vendes actualmente?",
                "¿Cuál es tu ticket promedio o precio unitario por venta?",
                "¿Cuántos clientes activos o transacciones tienes por mes?",
                "¿Cuál es tu principal canal de adquisición de clientes?",
                "¿Cuál es tu margen bruto estimado (porcentaje)?",
                "¿Cuál es tu oferta de valor principal y cómo está estructurada?",
                "¿Cuál es tu capacidad operativa máxima antes de necesitar contratar?",
                "¿Cuál es el mercado geográfico objetivo principal?",
                "¿Qué activos existentes tienes (audiencia, base de datos, marca, etc.)?"
            ]
        elif goal_type == "technical":
            return [
                "¿Cuál es la stack tecnológica principal?",
                "¿Existen tests automatizados actualmente?",
                "¿Cuál es el principal cuello de botella técnico?",
                "¿Qué deuda técnica identificas como la más crítica?"
            ]
        elif goal_type == "operations":
            return [
                "¿Qué tareas repetitivas consumen más del 20% de tu tiempo semanal?",
                "¿Qué herramientas de software usas actualmente para gestionar operaciones?",
                "¿Dónde ocurren las principales fallas de comunicación o cuellos de botella?"
            ]
        else:
            return [
                "¿Cuáles son los plazos esperados para alcanzar este objetivo?",
                "¿Qué métricas clave definirán el éxito de esta meta?",
                "¿Qué recursos (presupuesto, personal, tiempo) tienes asignados?"
            ]
export_generator = StrategicQuestionGenerator
