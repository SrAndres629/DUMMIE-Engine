Feature: Ollama GPU Acceleration
  As a DUMMIE Engine operator
  I want Ollama to serve LLM models on the NVIDIA GPU
  So that local inference is 10-100x faster than CPU

  Scenario: Ollama service starts on GPU
    Given NVIDIA driver 595.71.05 is loaded
    And CUDA 13.2 is available
    When ollama service is enabled and started
    Then ollama serve must use CUDA
    And GPU memory usage exceeds 100 MiB

  Scenario: All required models are pre-pulled
    Given ollama is running on port 11434
    When checking available models
    Then gemma4:e2b, gemma4:e4b, gemma3:1b, qwen3-embedding are listed

  Scenario: VRAM stays within budget
    Given ollama is running with models loaded
    When checking nvidia-smi
    Then used VRAM must not exceed 5120 MiB
