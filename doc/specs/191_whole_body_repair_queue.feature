Feature: Whole Body Repair Queue
  As a Metacognitive Repair Planner,
  I want to translate systemic body gaps into a prioritized action queue,
  So that DUMMIE repairs its structural integrity in a safe, order-of-operations sequence.

  Scenario: Compiling and prioritizing repair actions
    Given a list of capability governor and operational auditor findings
    When the whole body repair queue compiles actions
    Then it should sort actions by priority
    And it should prioritize false READY claims and Kùzu readback before new features
    And it should write the latest repair queue reports
