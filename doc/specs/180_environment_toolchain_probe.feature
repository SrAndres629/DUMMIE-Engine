Feature: Environment Toolchain Probe
  As a Metacognitive Infrastructure Auditor,
  I want to safely probe the host polyglot compilers and interpreters,
  So that I have precise awareness of available build/test ecosystems.

  Scenario: Probe of available toolchains
    Given a need to profile the host environment políglota
    When the environment toolchain probe runs
    Then it should query versions for python3, go, rustc, cargo, elixir, node
    And it should identify which toolchains are missing
    And it should compile a decision of PASS_WITH_WARNINGS if optional toolchains are missing
    And it should write the latest toolchain reports
