Feature: Dummie SDK Core Functionality
  As a Principal Engineer
  I want a fully typed, streaming SDK
  To automate complex reasoning workflows safely.

  Scenario: Conexión exitosa y ejecución de intención
    Given el motor DUMMIE está activo en L0 y L1
    When el usuario inicializa `dummie.Client()`
    And despacha la intención "Auditar seguridad de L3"
    Then el servidor debe retornar un `transaction_id` válido
    And habilitar el streaming bidireccional de eventos.
