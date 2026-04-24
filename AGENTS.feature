Feature: Agent Collaboration Discipline
  As a multi-agent team
  I want explicit ownership and validation evidence
  So that concurrent work remains consistent and auditable

  Scenario: agent handoff includes evidence
    Given an agent finishes a task slice
    When it hands off to another agent
    Then changed files, assumptions, and validation evidence are included

  Scenario: conflicting edits are resolved deterministically
    Given two agents propose different changes
    When integration happens
    Then deterministic checks and lower complexity decide acceptance
