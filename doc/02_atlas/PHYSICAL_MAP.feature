Feature: Physical Topography Validation
  As a Systems Auditor
  I want to verify that the physical layout matches the architectural design
  In order to maintain environmental sovereignty and data integrity

  Background:
    Given the monorepo follows the "Sustrato Dividido" policy
    And Layer 0 (Elixir) is the top-level supervisor

  Scenario: Validate Layer Directory Structure
    When I scan the "layers/" directory
    Then I should find directories for L0, L1, L2, L3, and L4
    And each directory must contain a valid build manifest (mix.exs, main.go, pyproject.toml, Cargo.toml, build.zig)
    And Performance Metric: layout_compliance == 1.0

  Scenario: Verify Telemetry Path Existence
    When I check the system mount points
    Then I should find "/media/datasets/dummie/telemetry"
    And the path must be writable by the L1 (Nervous) system
    And Performance Metric: telemetry_ready == 1.0
