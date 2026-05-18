Feature: EmbeddingMesh Foundation and Repo Self-Knowledge
  As a principal agentic systems architect
  I want a sovereign, typed, multi-capability, and offline-resilient embedding mesh
  So that the repository can self-perceive and generate an actionable structural matrix.

  Scenario: A request is processed with offline fallback safety
    Given the FastEmbed library is unavailable
    When I request a TEXT_FAST embedding for content "DUMMIE Engine structural mapping"
    Then the registry should resolve the request using a DeterministicFallbackProvider
    And the response vector should be unit-normalized with 384 dimensions
    And the vector_space should be "fallback_hash_384"
    And degraded should be true

  Scenario: Scanned files are routed and classified
    Given the EmbeddingRouter routes files
    When a file named "layers/l2_brain/model_router.py" is evaluated
    Then the ContentType should be CODE
    And the EmbeddingCapability should be CODE

    When a file named "doc/specs/192_embedding_mesh_foundation.md" is evaluated
    Then the ContentType should be SPEC
    And the EmbeddingCapability should be TEXT_FIDELITY

  Scenario: Reranker rejects vector space collisions
    Given a query in vector space "custom_2d"
    And a candidate in vector space "different_space_3d"
    When the HybridReranker scores the candidate
    Then it should not perform vector cosine similarity on the candidate
    And the score should rely solely on exact token overlap and metadata boosts/penalties
