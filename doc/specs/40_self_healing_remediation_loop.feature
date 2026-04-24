Feature: Bucle de Autosanación e Infraestructura (DE-V2-L4-40)
  Criterios de Aceptación Ejecutables para el Sistema de Remediación.

  Scenario: Autonomous Latency Remediation
    Given a microservice with latency > 500ms (detected via L6 OTel)
    When the Self-Healing Agent analyzes the RCA
    And it determines a "Resource_Scaling" is required
    Then it must increase the Pod replicas in the Kubernetes manifest
    And it must update the "Infra_Drift" ledger
    And Performance Metric: remediation_loop_time < 30s

  Scenario: Circuit Breaker on Recursive Failures
    Given a service with 3 remediations in the last 24h
    When a 4th failure is detected
    Then the Self-Healing system must deactivate for this node
    And it must trigger a "CRITICAL_FAILURE" alert in the Command Canvas (L6)
    And it must request manual inspection from the PAH
    And Performance Metric: CB_activation < 1s
