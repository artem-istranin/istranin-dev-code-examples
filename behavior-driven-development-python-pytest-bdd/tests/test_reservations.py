"""Connect agreed reservation examples to the inventory's public interface."""

from pytest_bdd import given, parsers, scenarios, then, when

from inventory import Inventory, OutOfStockError

scenarios("features/reservations.feature")


@given(parsers.parse("a booking has {available:d} seats available"), target_fixture="inventory")
def available_inventory(available: int) -> Inventory:
    """Give each scenario its own available seats."""
    return Inventory(available=available)


@given(parsers.parse("an earlier customer has reserved {quantity:d} seats"))
def earlier_reservation(inventory: Inventory, quantity: int) -> None:
    """Establish prior booking history through the same public operation."""
    inventory.reserve(quantity)


@when(parsers.parse("a customer requests {quantity:d} seats"), target_fixture="reservation_error")
def request_seats(inventory: Inventory, quantity: int) -> OutOfStockError | ValueError | None:
    """Capture expected rejections; unexpected errors still fail the scenario."""
    try:
        inventory.reserve(quantity)
    except (OutOfStockError, ValueError) as error:
        return error
    return None


@then("the reservation is accepted")
def reservation_accepted(reservation_error: OutOfStockError | ValueError | None) -> None:
    """An accepted request has no domain rejection."""
    assert reservation_error is None


@then("the reservation is rejected because there are not enough seats")
def insufficient_seats(reservation_error: OutOfStockError | ValueError | None) -> None:
    """Rejection communicates the availability boundary."""
    assert isinstance(reservation_error, OutOfStockError)


@then("the reservation is rejected because the quantity must be positive")
def invalid_quantity(reservation_error: OutOfStockError | ValueError | None) -> None:
    """Rejection communicates the positive-quantity requirement."""
    assert isinstance(reservation_error, ValueError)


@then(parsers.parse("{remaining:d} seats remain available"))
def remaining_seats(inventory: Inventory, remaining: int) -> None:
    """Observe remaining stock after both accepted and rejected requests."""
    assert inventory.available == remaining
