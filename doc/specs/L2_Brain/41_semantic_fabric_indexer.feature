Feature: Semantic Fabric Integrity Check
  Como el Nodo Arquitecto (L2)
  Quiero que mis especificaciones y decisiones (ADR) estén bidireccionalmente vinculadas
  Para evitar desincronización cognitiva y alucinaciones por contexto aislado

  Scenario: Validación de enlace ADR hacia Spec
    Given un nuevo ADR propuesto en "doc/01_architecture/adr/"
    And el ADR contiene una referencia a la spec "DE-V2-L2-41"
    When el Semantic Fabric Indexer escanea el repositorio
    Then la spec "DE-V2-L2-41" debe existir
    And el indexador debe actualizar el "ontological_map.json" confirmando el cruce semántico

  Scenario: Desactivación de Fitness Functions en ADRs revocados
    Given un ADR "0002-old-decision.md" con "status: SUPERSEDED" en su frontmatter
    And el ADR tiene un archivo hermano "0002-old-decision.rules.json"
    When el Semantic Fabric Indexer consolida las reglas de arquitectura
    Then el archivo "0002-old-decision.rules.json" debe ser purgado del "Active Constraint Payload"
    And las restricciones de ese ADR ya no deben afectar al Agente 3 (Tech Lead)

  Scenario: Detección de orfandad en el Memory Ledger
    Given una resolución "RES-099" en ".aiwg/memory/resolutions.jsonl"
    When el Indexador revisa las dependencias hacia las Specs
    And no encuentra ninguna Spec que justifique "RES-099"
    Then lanza una alerta "Orphaned Memory Detected" al Metacognitive Audit Loop
