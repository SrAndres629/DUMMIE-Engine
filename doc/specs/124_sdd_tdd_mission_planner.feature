Feature: Mission Planner
  As a Strategic Planner
  I want to break down goals into actionable phases
  So that execution is governed by SDD and TDD.

  Scenario: Plan from phase seed
    Given a next_phase_seed with required outputs
    When the MissionPlanner executes
    Then it should produce an L1 objective
    And it should create L2 phases for each output
    And it should inject TDD requirements.
