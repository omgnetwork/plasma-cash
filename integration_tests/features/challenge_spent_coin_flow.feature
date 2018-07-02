Feature: Challenge spent coin flow

  Scenario: userA deposits to plasma cash and transfers to userB. userB transfers to userC and tries to withdraw the funds. Then userC challenges the exit.
    Given userA deposits 1 eth in plasma cash
    And userA transfers 1 eth to userB
    And userB transfers 1 eth to userC
    When userB starts to exit 1 eth from plasma cash
    Then root chain got the start-exit record from coin spent challenge
    When userC challenges the coin spent exit
    Then the challenge is successful and root chain cancels the coin spent exit
