Feature: Cognitive Lifecycle Contract
  The DUMMIE runtime must resolve truth through canonical evidence before high-confidence answers or mutations.

  Scenario: Architecture answer without evidence is blocked from high confidence
    Given an agent is asked to decide an architecture direction
    And the only source is a chat transcript
    When CognitiveLifecycleContract preflight runs
    Then the decision is REQUIRES_HUMAN_REVIEW or BLOCK
    And the confidence is UNKNOWN or REQUIRES_HUMAN
    And an EvidenceReceipt is required

  Scenario: Advisory mode produces real receipts
    Given advisory mode is enabled
    And an entrypoint asks for an action with missing evidence
    When CognitiveLifecycleContract preflight runs
    Then the decision is ADVISORY_ONLY
    And the report records the action that would have been blocked
    And postflight writes a valid EvidenceReceipt

  Scenario: Code mutation requires semantic discovery
    Given a request has operation_class code_mutation
    And Socraticode discovery has not been recorded
    When CognitiveLifecycleContract preflight runs
    Then the decision is BLOCK
    And the next_action is run semantic discovery and blast radius analysis

  Scenario: Degraded persistence cannot become pass
    Given a request writes persistent memory
    And Kuzu persistence is DEGRADED
    When CognitiveLifecycleContract postflight runs
    Then the status is BLOCKED or FAILED
    And the receipt does not contain degraded_success

  Scenario: PACK R3 promotion requires lifecycle enforcement
    Given a request has risk_level R6_PACK
    And the L2 runtime lacks CognitiveLifecycleContract integration
    When CognitiveLifecycleContract preflight runs
    Then the decision is BLOCK
    And the next_action is implement lifecycle enforcement in advisory mode first

