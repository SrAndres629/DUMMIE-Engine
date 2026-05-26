Feature: sched_ext Layered Scheduler
  As a DUMMIE Engine operator
  I want sched_ext scx_layered to assign different policies by layer
  So that L0 gets real-time priority, L1 is latency-sensitive, L2 is throughput

  Scenario: sched_ext scx_layered is loaded
    Given kernel supports CONFIG_SCHED_CLASS_EXT
    When scx_layered is installed and the service starts
    Then /sys/kernel/sched_ext/ops shows "layered"

  Scenario: Layer-specific scheduling
    Given scx_layered is active
    When processes in agentic-workload.slice are running
    Then L0 overseer processes get SCHED_EXT with real-time policy
    And L1 gateway processes get SCHED_EXT with latency-sensitive policy
    And L2 brain processes get SCHED_EXT with throughput policy

  Scenario: Graceful fallback
    Given sched_ext modules are not available
    When scx_layered fails to load
    Then all processes continue under default CFS scheduler
    And no system crash occurs
