Feature: Long-Running Mission Runtime
  As DUMMIE
  I want multi-phase missions to survive context loss
  So that work can continue across long sessions

  Scenario: runtime delegates to ledger
    Given a mission runtime operation
    Then lifecycle state is recorded through `PhaseLedger`

  Scenario: dependencies are enforced
    Given a phase depends on an incomplete phase
    When the dependent phase starts
    Then the runtime records a blocked phase event

  Scenario: daemon outcome can include mission state
    Given daemon mission runtime is available
    Then daemon outcomes can include reconstructed current mission state
