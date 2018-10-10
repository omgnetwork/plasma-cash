Feature: Exit deposit flow

  Scenario: userA deposits to plasma cash and then tries to exit the deposit
    Given userA deposits 1 eth in plasma cash
    When userA starts to exit 1 eth from plasma cash
    Then root chain got the start-deposit-exit record
    When two weeks have passed from depositing exit
    And userA finalize the deposit exit
    Then userA has around 100 eth in root chain after exit
