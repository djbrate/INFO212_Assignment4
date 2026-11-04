"""Order rules: state machine (DR-1, FR-A3.3), total (DR-3), validation (FR-C3.4)."""
from datetime import date, timedelta

import pytest

from app.models.enums import OrderStatus as S
from app.models.enums import PaymentStatus
from app.models.order import GuestGroupNote, InvalidTransition, Order, OrderItem
from app.models.validation import ValidationError

TODAY = date(2026, 11, 4)


def make_order(**kw):
    data = dict(customer_id="c1", event_date=TODAY + timedelta(days=10), guests=20,
                delivery_address="Bryggen 1, Bergen",
                items=[OrderItem("f1", "Fish soup", 20, 189), OrderItem("f2", "Salad", 10, 165)])
    data.update(kw)
    return Order(**data)


def test_new_order_is_submitted_and_not_paid():
    order = make_order()
    assert order.status == S.SUBMITTED
    assert order.payment_status == PaymentStatus.NOT_PAID


def test_total_is_calculated_from_lines():
    assert make_order().total == 20 * 189 + 10 * 165


@pytest.mark.parametrize("path", [
    [S.APPROVED, S.IN_PREPARATION, S.DELIVERED],
    [S.REJECTED],
    [S.APPROVED, S.REJECTED],
    [S.CANCELLED],
    [S.APPROVED, S.CANCELLED],
    [S.APPROVED, S.IN_PREPARATION, S.CANCELLED],
])
def test_allowed_transitions(path):
    order = make_order()
    for status in path:
        order.change_status(status)
    assert order.status == path[-1]


@pytest.mark.parametrize("path, bad", [
    ([], S.DELIVERED),                      # cannot skip steps
    ([], S.IN_PREPARATION),
    ([S.APPROVED, S.IN_PREPARATION], S.REJECTED),
    ([S.APPROVED, S.IN_PREPARATION, S.DELIVERED], S.CANCELLED),  # delivered is final
    ([S.REJECTED], S.APPROVED),             # rejected is final
    ([S.CANCELLED], S.SUBMITTED),           # cancelled is final
])
def test_forbidden_transitions(path, bad):
    order = make_order()
    for status in path:
        order.change_status(status)
    with pytest.raises(InvalidTransition):
        order.change_status(bad)


def test_valid_order_passes():
    make_order(notes=[GuestGroupNote("nut allergy", 2)]).validate(TODAY)


@pytest.mark.parametrize("kw, message", [
    ({"event_date": TODAY}, "future"),
    ({"event_date": TODAY - timedelta(days=3)}, "future"),
    ({"guests": 0}, "between 1"),
    ({"guests": 5000}, "between 1"),
    ({"delivery_address": " "}, "address"),
    ({"items": []}, "no items"),
    ({"notes": [GuestGroupNote("vegan", 30)]}, "more guests"),
    ({"notes": [GuestGroupNote("", 2)]}, "description"),
])
def test_invalid_orders_are_rejected(kw, message):
    with pytest.raises(ValidationError) as err:
        make_order(**kw).validate(TODAY)
    assert message in str(err.value)
