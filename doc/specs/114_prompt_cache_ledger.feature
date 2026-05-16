Feature: Prompt cache ledger
  Scenario: Append idempotent record
    Given a frame_id already exists in the ledger
    When record_frame runs again
    Then no duplicate line is added

  Scenario: Reusable frame lookup
    Given matching mission phase source hash and receipt
    When find_reusable_frame is called
    Then reusable frame is returned

  Scenario: Invalidate on source hash mismatch
    Given source hash changed
    When find_reusable_frame is called
    Then no reusable frame is returned
