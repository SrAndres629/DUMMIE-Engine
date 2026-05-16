Feature: PolyglotArchitectureRegistry
  As DUMMIE governance
  I want a canonical layer-language registry
  So that global reasoning does not collapse into Python-only summaries

  Scenario: Global architecture audit loads polyglot registry
    Given a global architecture audit starts
    When context is selected
    Then polyglot registry and layer language map are loaded

  Scenario: Python-only summary is rejected for global project review
    Given a global project review is requested
    When the summary covers only Python or L2
    Then the summary is rejected as incomplete

  Scenario: Vendored dependency files do not define first-party architecture
    Given dependency or generated files are tracked
    When architecture identity is computed
    Then dependency and generated files are excluded from first-party identity

  Scenario: Layer map includes all L0-L6 layers or records low-confidence gaps
    Given the layer map is generated
    Then layers L0 through L6 are represented
    And sparse layers are marked low confidence

  Scenario: ProjectWorldModel consumes layer_language_map
    Given P7 begins
    When project world model inputs are loaded
    Then layer_language_map is consumed

  Scenario: SpecCoverageGate uses registry to require layer/language coverage
    Given P8 validates spec coverage
    When global coverage is evaluated
    Then layer and language coverage are checked through the registry

  Scenario: ContextQuant prefers compact registry over raw repo scan
    Given ContextQuant needs architecture context
    When context is selected
    Then compact registry artifacts are preferred over raw repo dumps

  Scenario: Unknown language ownership triggers audit warning
    Given a language appears without clear owner layer
    When registry validation runs
    Then an audit warning is recorded
