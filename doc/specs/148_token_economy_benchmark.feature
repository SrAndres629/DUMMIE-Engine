Feature: Token Economy Benchmark
  Scenario: Compare all strategies
    Given a repository with known file sizes
    When the benchmark runs
    Then at least 5 strategies must be compared
    And raw_folder_naive_estimate must have more tokens than memory_spine_plus_selected_dossiers
    And measurement_type must be deterministic_estimate
