Feature: L2 Brain Bounded Context Segregation
  Como el Nodo de Arquitectura
  Quiero asegurar que L2_Brain esté subdividido exactamente en 4 Bounded Contexts
  Para evitar el acoplamiento y el código espagueti en el Dominio Puro

  Scenario: Creación de un contexto no autorizado
    Given el directorio "layers/l2_brain/src/brain/domain/"
    When el Agente intenta crear una carpeta "utils"
    Then el Semantic Fabric Indexer debe bloquear la acción
    And el error debe indicar que solo ["context", "memory", "fabrication", "governance"] están permitidos

  Scenario: Aislamiento estricto de contextos
    Given un archivo en "layers/l2_brain/src/brain/domain/memory/storage.py"
    When el código intenta importar directamente desde "layers/l2_brain/src/brain/domain/fabrication/builder.py" sin usar un puerto
    Then el validador estático (LST Scanner) debe lanzar una advertencia de violación de aislamiento
