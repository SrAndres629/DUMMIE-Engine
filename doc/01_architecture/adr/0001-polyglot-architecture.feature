Feature: Polyglot Architecture Enforcement
  Como el Validador Arquitectónico (Sentinel)
  Quiero asegurar la especialización radical de lenguajes por capa
  Para garantizar la integridad y rendimiento del ecosistema híbrido

  Scenario: Violación de lenguaje en L3
    Given el directorio de la capa "layers/l3_shield"
    When el Agente intenta crear un archivo "security.py" (Python)
    Then el validador debe bloquear la operación
    And emitir un error "L3_Shield strictly requires Rust (.rs)"

  Scenario: Comunicación Inter-Capa Aprobada
    Given un componente en "L1_Nervous" y otro en "L2_Brain"
    When intentan compartir un tensor masivo
    Then el protocolo utilizado debe ser "arrow" (Apache Arrow Zero-Copy)
    And no se debe utilizar serialización JSON
