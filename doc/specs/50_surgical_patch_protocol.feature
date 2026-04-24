Feature: Protocolo de Parche Quirúrgico (DE-V2-L5-50)
  Criterios de Aceptación Ejecutables para el Diffeo Atómico y la Integridad de Archivos.

  Scenario: Apply a clean patch with matching hash
    Given an agent proposing a patch for "utils.go"
    And the Target Hash is "a1b2c3d4"
    When the L5 Muscle verifies that the current file hash matches "a1b2c3d4"
    Then the patch must be applied to the specified line range
    And the Performance Metric: patch_application_latency < 5ms
    And the Performance Metric: integrity_errors == 0

  Scenario: Reject patch due to hash mismatch (User drift)
    Given an agent proposing a patch for a file the user just edited
    When the L5 Muscle detects a hash mismatch
    Then the patch must be Vetoed immediately
    And the agent must receive a "DESYNC_ERROR"
    And the Performance Metric: validation_latency < 1ms

  Scenario: Atomic multi-file patch
    Given a task requiring patches in "spec.md" and "code.go"
    When the first patch fails during validation
    Then neither "spec.md" nor "code.go" must be modified
    And the Performance Metric: atomicity_overhead < 10ms
