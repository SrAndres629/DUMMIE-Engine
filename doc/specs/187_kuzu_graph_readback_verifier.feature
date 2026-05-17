Feature: Kuzu Graph Readback Verifier
  As a Metacognitive Memory Spine Auditor,
  I want to verify Kùzu database integrity at three levels,
  So that DUMMIE's memory spine is robust, idempotent, and corruption-free.

  Scenario: Safely auditing loci.db readback and sandbox writes
    Given an operational Kùzu database path
    When the Kuzu graph readback verifier runs
    Then it should perform a safe sandbox write-and-readback test
    And it should verify node and edge counts on loci.db without altering production data
    And it should report a verified promotion recommendation of READY or READY_CANDIDATE
