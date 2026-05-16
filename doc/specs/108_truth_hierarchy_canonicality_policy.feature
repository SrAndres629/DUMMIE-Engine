Feature: Truth Hierarchy and Canonicality Policy
  As DUMMIE governance
  I want explicit truth precedence and conflict resolution
  So that context selection is evidence-driven and not recency-driven

  Scenario: Code with passing tests outranks stale spec
    Given source code has passing tests
    And an active spec is stale
    When truth conflict is resolved
    Then code and passing tests win

  Scenario: Active spec outranks unsupported report
    Given an active spec exists
    And a report has no supporting evidence
    When truth conflict is resolved
    Then the active spec wins

  Scenario: Report PASS claim loses to failed tests
    Given a report claims PASS
    And linked tests fail
    When conflict is resolved
    Then failed tests override the report claim

  Scenario: Chat claim cannot create truth without evidence
    Given chat claims a feature exists
    And repo has no supporting evidence
    When truth selection executes
    Then chat claim is non-canonical and rejected for high-confidence use

  Scenario: Obsidian mirror cannot override internal canonical source
    Given Obsidian mirror conflicts with internal canonical artifact
    When conflict is resolved
    Then internal canonical source wins

  Scenario: Stale vault entry is demoted
    Given a vault entry is active
    And its source hash changed
    When demotion rules apply
    Then vault entry becomes stale

  Scenario: Legacy doc referencing missing spec is low confidence
    Given a legacy doc references missing spec files
    When confidence is scored
    Then legacy doc is low-confidence source

  Scenario: Equal rank conflict requires freshness tie-break
    Given two artifacts share the same rank
    And one is fresh and one is stale
    When conflict is resolved
    Then fresher artifact wins

  Scenario: Unsafe artifact is rejected
    Given an artifact contains secrets or private reasoning
    When safety validation runs
    Then artifact is rejected immediately

  Scenario: Unknown freshness blocks high-confidence context
    Given artifact freshness is unknown
    When selecting high-confidence context
    Then artifact is excluded from high-confidence context
