Feature: FolderNotes and NotePlans governance
  Scenario: Folder note is derived and cannot override code/tests/specs
    Given a folder note exists for a tracked folder
    When the note conflicts with code tests or active specs
    Then canonical sources outrank the folder note

  Scenario: Folder note includes source hash and freshness status
    Given a folder note manifest entry
    Then it includes source_hash hash_method and freshness status

  Scenario: Folder note links to spec coverage matrix
    Given folder notes are generated
    Then the manifest references .aiwg/reports/spec_coverage_matrix.json

  Scenario: Folder note defaults to summary_only token role
    Given a new folder note
    Then token_role defaults to summary_only

  Scenario: Missing folder creates low-confidence/path-missing note
    Given a configured tier-0 folder path is absent
    Then note status is path_missing or low_confidence

  Scenario: NotePlan records future probes without implementing them
    Given a noteplan exists
    Then it lists future probes and stale triggers only

  Scenario: Source hash change requires refresh in P10
    Given a folder source hash changed
    Then P10 marks corresponding note stale

  Scenario: P11 may include folder note by reference, not raw folder
    Given context packaging is requested
    Then folder notes are included by reference and token policy

  Scenario: P13 uses notes as compression candidates
    Given context quantization runs
    Then folder notes are treated as derived compression candidates
