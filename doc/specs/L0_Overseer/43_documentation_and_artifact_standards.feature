Feature: Estándares de Documentación y Artefactos (DE-V2-L0-43)
  Criterios de Aceptación Ejecutables para el Ecosistema Documental.

  Scenario: Enforce Layer-Folder Physical Alignment
    Given a specification file with metadata "layer: L1"
    When the SDD Semantic Auditor scans the filesystem
    Then the file must reside in a directory named "L1_Nervous"
    And Performance Metric: validation_latency < 100ms

  Scenario: Auto-Repair Missing Sibling Files
    Given a mandatory specification in the Alpha Block (L0, L1)
    And the sibling ".feature" file is missing
    When the validator is executed
    Then it must automatically generate a ".feature" template
    And it must signal an "MSA Missing" warning
    And Performance Metric: template_generation_time < 1s

  Scenario: Validate Internal Link Consistency
    Given a hierarchical folder structure
    When the link synchronization script is executed
    Then all relative links "[...](...)" must point to valid file locations
    And there must be no broken cross-references in the doc/ tree.
    And Performance Metric: link_sync_latency < 5s
