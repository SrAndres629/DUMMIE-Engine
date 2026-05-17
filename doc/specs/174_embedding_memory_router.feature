Feature: Embedding Memory Router
  As a Semantic/Memory Router,
  I want to securely index and query 6D context items offline,
  So that DUMMIE can semantically retrieve memory nodes without compromising credentials.

  Scenario: Indexing context items offline using fallback projection
    Given a list of compiled 6D context items
    When the embedding memory router compiles the index
    Then it should activate DETERMINISTIC_FALLBACK mode
    And it should compute projection vectors without network calls
    And it should issue warning flags and write the embedding report
