Feature: Challenge double spending flow

  Scenario: userA first transfers to userB and then tries to double spend the same funds to userC. userC tries to withdraw the funds and userB challenges the exit.
    Given userA deposits 1 eth in plasma cash
    And userA transfers 1 eth to userB
    And userA tries to double spend 1 eth to userC
    When userC starts to exit 1 eth from plasma cash
    Then root chain got the start-exit record from double spending challenge
    When userB challenges the exit
    Then the challenge is successful and root chain cancels the exit
