Feature: Sovereign Secret Injection Protocol (DE-V2-L3-47)
  Criterios de Aceptación Ejecutables para la Ceguera Cognitiva de Secretos.

  Scenario: Blind injection into a Shell command
    Given a vault secret "GITHUB_TOKEN" in L3 Enclave
    And an agent "Coder" in Layer 2
    When the Coder generates a command "git push https://$VAULT_GITHUB_TOKEN@github.com/repo.git"
    Then the L2 Brain must only see the placeholder "$VAULT_GITHUB_TOKEN"
    And the L5 Muscle adapter must hydrate the command with the real token during execution
    And the Performance Metric: hydration_latency < 2ms
    And the Performance Metric: leak_probability == 0.0

  Scenario: Prevent secret leak via print/log
    Given an agent trying to dump environment variables
    When the agent issues a "print(env)" command
    Then any key matching a Vault secret must be redacted to "[REDACTED_VAULT_KEY]"
    And the Performance Metric: scrubbing_latency < 5ms

  Scenario: Restricted access by scope
    Given an agent "Researcher" with "READ_ONLY" scope
    When it attempts to invoke the placeholder "$VAULT_STRIPE_KEY" (Write-access)
    Then the L3 Shield must veto the request
    And a "Privilege_Violation" must be logged.
