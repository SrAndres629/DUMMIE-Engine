Feature: Dashboard L6 renderer
  Scenario: Build dashboard state
    Given runtime latest artifacts exist
    When dashboard state builder runs
    Then dashboard_l6_latest.json is parseable

  Scenario: Render dashboard HTML
    Given dashboard state exists
    When HTML rendering runs
    Then output includes current phase and flywheel decision

  Scenario: No external dependency required
    Given a local runtime environment
    When renderer runs
    Then no external frontend dependency is required
