Feature: Mission Orchestrator DAG
  As an Execution Coordinator
  I want to represent missions as dependency graphs
  So that the execution order is deterministic and safe.

  Scenario: DAG building
    Given a mission plan with sequential phases
    When the MissionOrchestratorDAG builds the graph
    Then it should create a START node
    And each phase should depend on the previous one
    And it should detect the next executable node.
