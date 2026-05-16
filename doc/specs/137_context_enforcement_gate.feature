Feature: Context Enforcement Gate
  As a Context Economy Guardian
  I want to gate access to the codebase
  So that token usage is minimized and dossiers are preferred.

  Scenario: Block raw folder load
    Given a request for raw folder scan
    When evaluated by ContextEnforcementGate
    Then the decision should be "BLOCK_RAW_FOLDER_BULK_LOAD"
    And reason should mention context waste.
