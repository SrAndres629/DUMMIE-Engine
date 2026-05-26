Feature: GPU-Accelerated Embedding Service
  As a DUMMIE Engine operator
  I want EmbeddingService to run on GPU
  So that embedding inference is 10-50x faster

  Scenario: EmbeddingService uses CUDA when available
    Given CUDAExecutionProvider is available (onnxruntime-gpu installed)
    When EmbeddingService().embed(["test query"]) is called
    Then the model runs on GPU
    And the result has 384 dimensions

  Scenario: EmbeddingService falls back to CPU gracefully
    Given CUDAExecutionProvider is NOT available
    When EmbeddingService().embed(["test query"]) is called
    Then the model runs on CPU
    And no exception is raised

  Scenario: Embedding dimensions are preserved
    Given the embedding service is initialized
    When embed is called with any text
    Then dimensions property returns 384
