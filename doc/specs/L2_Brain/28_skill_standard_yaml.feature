Feature: Estándar de Habilidades Agénticas (DE-V2-L2-28)
  Criterios de Aceptación Ejecutables para el Andamiaje y Validación de Skills.

  Scenario: Scaffold a new Skill autonomously
    Given the agent detects a missing "WebSearch" capability
    When it generates a directory "skills/web_search"
    And it writes a valid "SKILL.md", ".feature" and ".rules.json"
    Then the S-Shield must validate the new scaffold
    And the skill must be available for "ao.v2.diag.system_sanity" check
    And the Performance Metric: scaffolding_latency < 500ms
    And the Performance Metric: audit_pass_rate == 1.0

  Scenario: Hot-load a new skill without restart
    Given a new valid skill scaffold in "skills/web_search"
    When the Librarian agent performs a directory scan
    Then the skill "ao.v2.worker.web_search" must be indexed in KùzuDB
    And it must be available for invocation immediately
    And the Performance Metric: indexing_latency < 50ms
