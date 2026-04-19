Feature: Personalidad y Persistencia del Alma (DE-V2-L0-33)
  Criterios de Aceptación Ejecutables para la Identidad Evolutiva y el Soul Shifting.

  Scenario: Shift soul to Security Auditor persona
    Given an active session with "Creative Writer" soul
    When the system requirements shift to "Perform Security Audit"
    And the agent triggers a "Soul Shift" to "Security-Auditor" template
    Then the 6D Context Model must update its biases to "High_Security_Skepticism"
    And the agent's tone must become "Rigorous and Analytical"
    And the Performance Metric: persona_switch_latency < 100ms
    And the Performance Metric: bias_update_accuracy == 1.0

  Scenario: Evolution of the SOUL.md after learning
    Given a learning hito in the Necro-Learning pipeline
    When the agent reflect on its previous performance
    Then it must append a "Hito de Aprendizaje" to the SOUL.md
    And the "Mood" hyperparameter must be updated based on efficiency.
