Feature: Cognitive Artifact Protocol governance
  As DUMMIE governance
  I want lifecycle/canonicality/truth controls
  So that artifacts are safe and reliable in cognition

  Scenario: Candidate artifact becomes active only after verification
    Given an artifact in candidate state
    And required metadata is present
    When evidence and validations are completed
    Then lifecycle state can progress to verified
    And only then can it become active

  Scenario: Stale source hash demotes active artifact to stale
    Given an active artifact with source hashes
    When a linked source hash changes
    Then the artifact is demoted to stale

  Scenario: Obsidian mirror cannot override canonical internal vault
    Given an Obsidian-exported mirror artifact
    And a canonical internal artifact exists
    When conflict resolution is evaluated
    Then canonical internal artifact has precedence

  Scenario: Report with evidence remains derived unless promoted
    Given a report artifact with evidence refs
    When no explicit promotion decision exists
    Then canonicality remains derived

  Scenario: Secret-bearing artifact is rejected
    Given an artifact contains secret or credential material
    When security validation runs
    Then artifact lifecycle becomes rejected
    And artifact is invalidated immediately

  Scenario: Artifact without freshness cannot enter high-confidence context
    Given an artifact with freshness status unknown
    When selecting high-confidence context
    Then artifact is excluded from high-confidence context set

  Scenario: Higher truth rank wins conflict
    Given two conflicting artifacts
    And one has higher truth rank
    When conflict resolution executes
    Then the higher truth rank artifact wins
