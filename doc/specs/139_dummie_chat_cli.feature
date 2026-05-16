Feature: DUMMIE Chat CLI
  As a User
  I want to interact with the system
  So that I can get status and debt summaries quickly.

  Scenario: Show technical debt
    When I run "dummie-chat show technical debt"
    Then the response should summarize debt findings.
