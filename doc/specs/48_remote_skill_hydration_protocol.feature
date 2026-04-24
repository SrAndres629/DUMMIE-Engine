Feature: Remote Skill Hydration Protocol (DE-V2-L4-48)
  Criterios de Aceptación Ejecutables para la Adquisición Remota de Habilidades.

  Scenario: Hydrate a verified skill from GitHub
    Given a remote skill URL "https://github.com/dummie-engine/web-tools"
    When the Edge Gateway fetches the repository into the sterile zone
    And the Sentinel L3 audits the contract and lints the code
    Then the skill must be moved to "skills/web_tools"
    And it must be available for the swarm immediately
    And the Performance Metric: hydration_latency < 2000ms
    And the Performance Metric: audit_time < 500ms

  Scenario: Rejection of malicious remote skill
    Given a remote skill containing a "rm -rf /" pattern in its logic
    When the Sentinel performs static analysis during hydration
    Then the download must be purged immediately
    And a "Critical_Security_Alert" must be emitted
    And the Performance Metric: scan_latency < 100ms

  Scenario: PAH Veto on new skill discovery
    Given a valid new skill scaffold downloaded from a non-whitelisted domain
    When the PAH receives a "PENDING_HYDRATION" alert
    And the PAH clicks "VETO"
    Then the skill must NOT be installed in the production directory.
