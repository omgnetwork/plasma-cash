Feature: Challenge history flow

  Scenario: userA transfers funds to userB, userB transfers to userC, and userC transfers to userD. userD starts an exit and userB challenges the history. Then userD responds to the history challenge.
    Given userA deposits 1 eth in plasma cash
    And userA transfers 1 eth to userB
    And userB transfers 1 eth to userC
    And userC transfers 1 eth to userD
    When userD starts to exit 1 eth from plasma cash
    Then root chain got the start-exit record from history challenge
    When userB challenges the exit history with deposit tx
    Then root chain got the challenge record
    When userD responds to the history challenge
    Then root chain cancels the challenge
