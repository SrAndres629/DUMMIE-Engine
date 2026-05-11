Feature: Industrial Gear Integration Governance

  Scenario: Verify Gear Registration
    Given a new gear is proposed
    When the gear is added to shared/gear_registry.json
    Then it must have a defined "layer" (L0-L6)
    And it must have a "resource_profile" (Light, Medium, Heavy)
    And it must have a "connectivity_standard" (MCP, CLI, API)
