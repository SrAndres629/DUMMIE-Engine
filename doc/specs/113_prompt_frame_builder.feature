Feature: Prompt frame construction
  Scenario: Build prompt frame from quantized context
    Given a quantized context result exists
    When prompt frame builder runs
    Then a parseable prompt frame JSON is generated

  Scenario: Required references are preserved
    Given required context refs are present
    When prompt frame is built
    Then required refs remain in context_refs

  Scenario: Raw repo dump is blocked
    Given a raw root-like reference appears
    When prompt frame builder validates refs
    Then it rejects the frame build

  Scenario: Secret or private reasoning is rejected
    Given secret-like or private reasoning text is present
    When prompt frame builder validates content
    Then it raises an error
