Feature: Project Personality Adherence
  Como el Orquestador
  Quiero que el enjambre asimile los traits definidos en identity.json
  Para mantener una comunicación profesional, asertiva y contextualmente alineada

  Scenario: Ingesta obligatoria de Identidad
    Given el inicio de una nueva sesión cognitiva
    When el agente se inicializa
    Then debe cargar y aplicar ".aiwg/identity.json" antes de ejecutar el Prompt Maestro
    And sus respuestas deben reflejar los "traits" activos en la configuración

  Scenario: Bloqueo de Alucinación Discursiva
    Given un prompt del PAH solicitando una tarea
    When el Agente intenta responder con disculpas excesivas o muletillas de IA genérica
    Then el validador (si está activo en L6) debe advertir sobre la desviación del "tone of voice"
