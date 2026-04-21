Feature: Document Navigation Atlas
  As a Sovereign Agent
  I want to navigate the project documentation hierarchy
  In order to maintain architectural consistency and zero entropy

  Background:
    Given the system follows Hierarchical Sovereign Documentation (HSD)
    And the current root is /doc/

  Scenario: Verify Documentation Map Integrity
    When I scan the /doc/ directory
    Then I should find all primary loci defined in ATLAS.md
    And Performance Metric: navigation_latency < 100ms
    And Performance Metric: index_completeness == 1.0
