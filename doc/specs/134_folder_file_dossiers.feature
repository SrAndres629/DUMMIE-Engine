Feature: Folder and File Dossiers
  As a Context Manager
  I want to summarize folders and files
  So that context can be loaded efficiently.

  Scenario: Generate folder index
    When FolderDossierGenerator runs
    Then an index JSON should be produced
    And it should contain key folders.
