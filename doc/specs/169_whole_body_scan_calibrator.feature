Feature: Whole-Body Scan Calibration
  As a Metacognitive Runtime Engineer,
  I want to validate that scanner metrics and timings are fully calibrated,
  So that the DUMMIE Engine operates with verified sensory information.

  Scenario: Calibrator verifies successful scan metrics
    Given a fresh whole-body scanner execution report
    When the whole-body scan calibrator executes
    Then the calibrator should parse metrics from the scanner output
    And it should verify timing performance is under 8 seconds
    And it should assert schema conformance
    And it should output a calibration status of PASS

  Scenario: Calibrator detects mismatch and emits PASS_WITH_WARNINGS
    Given a scanner execution with unverified mock active elements
    When the whole-body scan calibrator executes
    Then it should flag unverified claims
    And it should emit PASS_WITH_WARNINGS and write the calibration reports
