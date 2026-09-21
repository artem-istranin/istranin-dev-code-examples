Feature: Reserve seats without overselling
  Customers can reserve available seats.
  Rejected requests leave the remaining seats available to other customers.

  Scenario Outline: Reserve a quantity that is available
    Given a booking has <available> seats available
    When a customer requests <quantity> seats
    Then the reservation is accepted
    And <remaining> seats remain available

    Examples:
      | available | quantity | remaining |
      | 3         | 2        | 1         |
      | 3         | 3        | 0         |

  Scenario Outline: Reject a request that exceeds availability
    Given a booking has <available> seats available
    When a customer requests <quantity> seats
    Then the reservation is rejected because there are not enough seats
    And <available> seats remain available

    Examples:
      | available | quantity |
      | 2         | 3        |
      | 0         | 1        |

  Scenario Outline: Reject a quantity that is not positive
    Given a booking has 3 seats available
    When a customer requests <quantity> seats
    Then the reservation is rejected because the quantity must be positive
    And 3 seats remain available

    Examples:
      | quantity |
      | 0        |
      | -1       |

  Scenario: A later customer can reserve seats after a rejected request
    Given a booking has 3 seats available
    And an earlier customer has reserved 2 seats
    When a customer requests 2 seats
    Then the reservation is rejected because there are not enough seats
    And 1 seats remain available
    When a customer requests 1 seats
    Then the reservation is accepted
    And 0 seats remain available
