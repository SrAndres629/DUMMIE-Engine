Feature: Canonical Spec Binding Registry
  As a DUMMIE maintainer
  I want a single registry linking specs to physical files
  So that implementation and documentation stay synchronized from day one

  Scenario: Build canonical bindings from spec markdown files
    Given a repository with valid spec files in doc/specs
    When I run "python3 scripts/spec_registry_sync.py"
    Then ".aiwg/spec_registry/spec_bindings.yaml" should be generated
    And each entry should include spec path, feature path, rules path, and evidence paths

  Scenario: Detect missing physical evidence in strict mode
    Given at least one spec references a missing file
    When I run "python3 scripts/spec_registry_sync.py --strict"
    Then the command should fail with a non-zero exit code
