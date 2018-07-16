Feature: Basic flow

  Scenario: userA deposit to plasma cash and transfer to userB and then userB can successfully withdraw
    Given userA and userB has 100 eth in root chain
    When userA deposit 1 eth to plasma
    Then userA has around 99 eth in root chain
    And userA has 1 eth in the deposit tx in plasma cash
    When userA transfer 1 eth to userB in child chain
    Then userB has 1 eth in the transfer tx in plasma cash
    When userB start exit 1 eth from plasma cash
    Then root chain got userB start exit 1 eth
    When two weeks have passed
    And userB finalize the exit
    Then userB has around 101 eth in root chain after exit
