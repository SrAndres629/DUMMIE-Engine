Feature: ProjectWorldModel
  As DUMMIE governance
  I want a compact canonical world model
  So that future agents can orient globally without raw-repo reconstruction

  Scenario: Agent loads project world model before global audit
    Given a global audit task starts
    When context is prepared
    Then project_world_model.json is loaded first

  Scenario: Python-only global summary is rejected
    Given a global project summary request
    When the summary covers only Python or L2
    Then the summary is rejected for incomplete architecture coverage

  Scenario: Current position and next phase are read from canonical state
    Given phase execution begins
    When state is loaded
    Then current_position.json and next_phase_seed.json are used as canonical dynamic state

  Scenario: World model references polyglot registry instead of raw repo scan
    Given architecture context is needed
    When global orientation is assembled
    Then polyglot registry references are preferred over raw repo-wide file dumps

  Scenario: Reports are used as evidence but not primary truth
    Given conflicting report and code claims
    When truth hierarchy is applied
    Then reports remain evidence-only and cannot override stronger truth sources

  Scenario: Raw vault/memory is not bulk-loaded into prompt
    Given prompt context is assembled
    When memory artifacts are considered
    Then raw vault and memory dumps are excluded by default

  Scenario: P8 consumes world model to build spec coverage gate
    Given P8 starts
    When inputs are selected
    Then project world model is consumed alongside polyglot and truth schemas

  Scenario: Stale world model requires regeneration
    Given canonical plan or registry state changes
    When world model freshness is evaluated
    Then regeneration is required before high-confidence global use
