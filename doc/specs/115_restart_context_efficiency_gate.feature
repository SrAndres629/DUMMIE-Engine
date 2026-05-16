Feature: Restart and context efficiency gate
  Scenario: Restart gate passes with warnings on optional artifacts
    Given critical state files are valid
    When restart gate runs
    Then decision is PASS or PASS_WITH_WARNINGS

  Scenario: Restart gate fails on invalid critical JSON
    Given current_position is invalid JSON
    When restart gate runs
    Then decision is FAIL

  Scenario: Benchmark compares three strategies
    Given package receipt and quantized outputs exist
    When context efficiency benchmark runs
    Then raw_naive_estimate folder_notes_only and quantized_context_frame are reported
