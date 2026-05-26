Feature: tmpfs for .aiwg Ephemeral Data
  As a DUMMIE Engine operator
  I want .aiwg/runtime, .aiwg/reports, and .aiwg/sockets in tmpfs
  So that ephemeral I/O does not hit the NTFS FUSE layer

  Scenario: tmpfs mounts exist before engine start
    Given dummie-engine.service is about to start
    When ExecStartPre runs
    Then .aiwg/runtime is a tmpfs mount
    And .aiwg/reports is a tmpfs mount
    And .aiwg/sockets is a tmpfs mount

  Scenario: tmpfs mounts cleaned up after engine stop
    Given dummie-engine.service has stopped
    When ExecStopPost runs
    Then the tmpfs mounts are unmounted

  Scenario: Persistent .aiwg dirs remain on NTFS
    Given the system is running
    When checking other .aiwg subdirs
    Then .aiwg/identity, .aiwg/memory, .aiwg/heartbeat are NOT on tmpfs
