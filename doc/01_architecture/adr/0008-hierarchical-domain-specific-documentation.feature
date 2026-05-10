Feature: Estructura Jerárquica de Especificaciones
  Como Arquitecto L0
  Quiero que las especificaciones estén organizadas por capas (L0-L6)
  Para respetar los Bounded Contexts y el DDD

  Scenario: Archivo de especificación en ubicación incorrecta
    Given un archivo de especificación "doc/specs/L1_Nervous/10_protobuf_contracts.md"
    When el validador lee el frontmatter del archivo
    Then el valor "layer" debe coincidir con "L1" (L1_Nervous)
    And si el frontmatter indica "layer: L2", el validador debe emitir un error de "Misplaced Bounded Context"
