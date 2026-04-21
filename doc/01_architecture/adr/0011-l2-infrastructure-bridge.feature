Feature: L2 Python Bridge for KùzuDB Bootstrap
  Como Nodo de Ejecución (sw.plant.coder)
  Quiero usar el adaptador nativo de KùzuDB en Python (L2_Brain)
  Para tener memoria funcional antes de que los bindings de L4 (Zig) estén listos

  Scenario: Uso del adaptador temporal L2
    Given la base de datos "loci.db"
    When el Agente necesita persistir topología espacial
    Then debe usar el adaptador de Python en "layers/l2_brain/src/brain/infrastructure/"
    And este puente debe estar documentado como transitorio hasta que se complete la migración a L4
