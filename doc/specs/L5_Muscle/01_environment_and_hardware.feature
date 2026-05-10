Feature: Entorno Físico y Restricciones del Metal (DE-V2-L5-01)
  Criterios de Aceptación Ejecutables para la Estabilidad de Hardware.

  Scenario: Thermal Throttling Enforcement
    Given a GPU temperature > 85C
    When the E-Shield (L3) detects the thermal stress
    Then it must suspend the Mojo compute hilos
    And it must emit a "Hardware_Overheat_Protection" signal
    And Performance Metric: detection_latency < 100ms

  Scenario: Resource Quota Monitoring
    Given an agent exceeding the RAM quota of 4GB
    When the system performs the pre-flight audit
    Then the task must be rejected until RAM is freed or compressed
    And Performance Metric: quota_check_latency < 10ms
