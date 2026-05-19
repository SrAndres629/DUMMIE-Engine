Feature: L2 Brain Organ Migration Contract
  PACK R4 must make canonical organs the public runtime surface while keeping flat_brain only as legacy fallback.

  Scenario: Public L2 modules resolve outside flat_brain
    Given the L2 package is importable
    When public modules like layers.l2_brain.model_router are imported
    Then their module files are outside layers/l2_brain/flat_brain

  Scenario: Canonical organs do not import flat_brain directly
    Given the canonical organ directories exist
    When their Python files are scanned
    Then no canonical organ imports layers.l2_brain.flat_brain directly

  Scenario: flat_brain remains compatibility only
    Given legacy modules still exist in flat_brain
    When a module lacks a canonical organ equivalent
    Then the root bridge may fall back to flat_brain
    But new canonical organ code must not depend on that fallback

