Feature: TUI process monitor snapshot
  Scenario: Build monitor snapshot from latest outputs
    Given runtime latest artifacts exist
    When monitor snapshot is built
    Then process_monitor_latest.json is parseable

  Scenario: Render text includes phase information
    Given snapshot exists
    When text renderer runs
    Then output includes current phase and next phase

  Scenario: Missing optional artifact produces warnings
    Given optional latest reports are missing
    When monitor snapshot runs
    Then decision degrades with warnings without crash
