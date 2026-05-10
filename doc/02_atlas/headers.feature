Feature: Project Headers Index Validation
  As a Librarian Agent
  I want to ensure the Project Headers Index is synchronized with the filesystem
  In order to prevent broken links and architectural blindness

  Background:
    Given the documentation root is "doc/"
    And the index file is "doc/02_atlas/headers.md"

  Scenario: Verify ADR Count
    When I count the ADR files in "doc/01_architecture/adr/"
    Then the index table for ADRs must contain exactly that number of entries
    And each link must resolve to a physical file
    And Performance Metric: index_accuracy == 1.0

  Scenario: Verify Spec Layer Compliance
    When I check a spec entry in the index
    Then the "Layer" column must match the subfolder in "doc/specs/" (e.g., L2 in doc/specs/L2_Brain/)
    And Performance Metric: structural_consistency == 1.0
