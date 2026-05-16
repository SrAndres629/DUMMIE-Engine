Feature: CLI control plane runtime
  Scenario: Status command returns JSON result
    Given runtime latest artifacts exist
    When CLI runs status
    Then command returns PASS or PASS_WITH_WARNINGS JSON

  Scenario: Missing latest file does not crash
    Given a referenced latest file is missing
    When CLI runs a read command
    Then command returns PASS_WITH_WARNINGS with warning details

  Scenario: Compress context command writes output
    Given context package and prompt frame exist
    When CLI runs compress-context
    Then local_context_compression_latest.json is created
