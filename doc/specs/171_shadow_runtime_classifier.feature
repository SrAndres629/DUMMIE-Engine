Feature: Shadow Runtime Classifier
  As a Metacognitive Runtime Engineer,
  I want to classify shadow modules without modifying the filesystem,
  So that I can identify entrypoints and candidates for manual review safely.

  Scenario: Classifier categorizes CLI files correctly
    Given a list of shadow modules
    And one of the shadow modules is a CLI command entrypoint
    When the shadow runtime classifier runs
    Then it should classify the file under cli_entrypoint
    And it should recommend recommended_action as do_not_touch or ignore

  Scenario: Classifier handles legacy files
    Given a shadow module in a backup or deprecated path
    When the shadow runtime classifier runs
    Then it should classify it under legacy_candidate
    And it should recommend recommended_action as archive or ignore
