Feature: Semantic Retrieval Runtime
  Scenario: Retrieve context for a prompt
    Given a prompt
    When I request semantic retrieval for the prompt
    Then the runtime uses the adapter
    And returns a standardized packet including context refs and vault refs
