Feature: DevEx y Estrategia de Despliegue (DE-V2-L0-08)
  Criterios de Aceptación Ejecutables para la Hermeticidad del Entorno.

  Scenario: Detect Execution Path via Bootstrap
    Given a host environment with Docker but without Nix
    When the "bootstrap.sh" script is executed
    Then the "EXEC_PATH" must be set to "DOCKER_SOVEREIGN"
    And the "session_context.json" must be initialized with the detected state
    And Performance Metric: detection_latency < 2s

  Scenario: Hermetic Build in Docker
    Given a "DOCKER_SOVEREIGN" execution path
    When the agent triggers a polyglot build (L0, L1, L3, L4)
    Then the build must occur inside the "Dockerfile.builder" container
    And the host environment must remain uncontaminated by polyglot dependencies
    And Performance Metric: build_overhead_docker < 15%
