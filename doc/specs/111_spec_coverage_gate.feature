Feature: SpecCoverageGate
  As DUMMIE governance
  I want measurable coverage gates
  So that heavy implementation phases do not proceed on weak or stale specification links

  Scenario: Complete spec triplet passes integrity check
    Given a spec family has md, feature, and rules json files
    When integrity is evaluated
    Then triplet status is complete_triplet

  Scenario: Missing rules JSON is coverage warning or failure
    Given a spec family is missing rules json
    When coverage thresholds are evaluated
    Then gate result is warning or fail based on integrity ratio

  Scenario: First-party language without coverage triggers warning
    Given a first-party language has no linked spec references
    When language coverage is evaluated
    Then a coverage warning is recorded

  Scenario: Dependency-only language does not define architecture identity
    Given a language is dependency-only
    When language coverage is evaluated
    Then missing direct spec refs do not define architecture failure by default

  Scenario: Layer with no spec refs is weak coverage
    Given a layer has no linked spec references
    When layer coverage is computed
    Then layer coverage is weak or unknown with notes

  Scenario: Runtime capability with tests gains stronger coverage
    Given a capability has path-backed presence and linked tests
    When capability coverage is computed
    Then coverage is strong or partial depending on spec links

  Scenario: Legacy missing spec references are isolated as inherited debt
    Given missing spec references in mcp_server_usage guide are known legacy debt
    When gate decision is produced
    Then debt is marked inherited and not introduced by P8

  Scenario: P9 cannot create notes without coverage constraints
    Given P9 starts FolderNotes and NotePlans
    When prerequisites are loaded
    Then spec coverage matrix constraints are consumed

  Scenario: P13 must consume coverage matrix before context optimization
    Given P13 starts ContextQuantRuntime planning
    When optimization context is assembled
    Then spec coverage matrix is consumed as governance input
