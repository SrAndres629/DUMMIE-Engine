Feature: Chaos & Regression Testing
  As a Reliability Engineer
  I want to simulate system failures and unsafe requests
  So that I can verify DUMMIE's safety gates remain intact.

  Scenario: Detect env access vulnerability
    Given a scenario that simulates ".env" access
    When ChaosRegressionTester runs
    Then it should verify the request was "BLOCK"
    And the scenario result should be "PASS".

  Scenario: Fail report on unsafe allowance
    Given a scenario that allows an unsafe request
    When ChaosRegressionTester runs
    Then the decision should be "FAIL"
    And findings should record the regression risk.
