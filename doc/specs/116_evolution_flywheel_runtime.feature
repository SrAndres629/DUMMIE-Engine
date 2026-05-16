Feature: Evolution flywheel runtime decision
  Scenario: Continue next phase when signals are healthy
    Given restart gate passes and benchmark improves
    When evolution flywheel runs
    Then decision is continue_next_phase

  Scenario: Repair before next phase when gate fails
    Given restart gate fails
    When evolution flywheel runs
    Then decision is repair_before_next_phase or block_due_to_runtime_failure

  Scenario: Decision includes expected gains and tests
    Given flywheel decision is produced
    Then blocking reasons expected gains and required next tests are present
