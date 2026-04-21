Feature: Modular Spec Assembly (MSA) Enforcer
  Como Sistema de Validación (Sentinel)
  Quiero asegurar que toda especificación adopte el patrón de archivos hermanos
  Para facilitar el BDD y reducir el consumo de tokens

  Scenario: Detección de Spec huérfana
    Given un nuevo archivo de especificación "doc/specs/L2_Brain/99_test.md"
    When el validador de soberanía escanea el directorio
    Then debe requerir la existencia de "99_test.feature" y "99_test.rules.json"
    And si faltan, debe reportar un error de "Missing MSA Siblings"
