Feature: Diagram Generation (DE-V2-ARCH-01)

  Scenario: Generate a system context diagram from Loci Graph
    Given the Loci Graph contains 3 active components
    When I execute the skill "sw.arch.diagram_generator" with "source: loci"
    Then it must output a valid Mermaid C4Context diagram
    And the output must not contain forbidden tags from rules.json
    And a new entry must be added to ledger.jsonl with tick status SUCCESS
