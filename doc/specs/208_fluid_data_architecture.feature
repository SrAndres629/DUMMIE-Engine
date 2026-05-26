---
spec_id: "208_fluid_data_architecture"
title: "Fluid Data Architecture — Dummie Engine Pipeline Optimization"
status: "ACTIVE"
layer: "cross-layer"
last_verified_on: "2026-05-25"
---

Feature: Fluid Data Architecture
  As a DUMMIE Engine operator
  I want all computational data to flow through the fastest path
  So that inference, embeddings, and I/O are GPU- and RAM-accelerated

  Scenario: GPU inference activated
    Given Ollama is installed with CUDA support
    When the ollama service is enabled and started
    Then ollama serve listens on port 11434
    And GPU utilization exceeds 0%

  Scenario: Ephemeral .aiwg in RAM
    Given the system has sufficient RAM
    When dummie-engine starts
    Then .aiwg/runtime, .aiwg/reports, .aiwg/sockets are tmpfs mounts

  Scenario: GPU-accelerated embeddings
    Given torch with CUDA is available
    When EmbeddingService.embed() is called
    Then the model runs on CUDA device
    And embedding latency is <50ms per batch

  Scenario: sched_ext scheduler loaded
    Given kernel supports CONFIG_SCHED_CLASS_EXT
    When scx_layered is installed and started
    Then /sys/kernel/sched_ext/ops shows active scheduler
