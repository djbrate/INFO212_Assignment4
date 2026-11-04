"""Orders, order items and guest-group notes.

Sources: CLAUDE.md (Customer Site 3, Admin panel 3); requirements FR-C3.2–3.5,
FR-A3.3–3.4, DR-1 (state machine), DR-3 (calculated total), DR-4 (unique number);
inbox/GDPR note from consultant.txt (allergies per guest group, never per name).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from .enums import OrderStatus, PaymentStatus
from .validation import ValidationError, check_event_date, check_guests

# DR-1 / FR-A3.3. Delivered, rejected and cancelled are final.
ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.SUBMITTED: {OrderStatus.APPROVED, OrderStatus.REJECTED, OrderStatus.CANCELLED},
    OrderStatus.APPROVED: {OrderStatus.IN_PREPARATION, OrderStatus.REJECTED, OrderStatus.CANCELLED},
    OrderStatus.IN_PREPARATION: {OrderStatus.DELIVERED, OrderStatus.CANCELLED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.REJECTED: set(),
    OrderStatus.CANCELLED: set(),
}


class InvalidTransition(ValidationError):
    pass


@dataclass
class OrderItem:
    """One line of an order. Keeps the name and unit price at the time of ordering (DR-6)."""

    food_item_id: str
    name: str
    quantity: int
    unit_price: int

    @property
    def line_total(self) -> int:
        return self.quantity * self.unit_price


@dataclass
class GuestGroupNote:
    """Allergy or dietary note for a group of guests, e.g. "nut allergy" × 2 (FR-C3.3)."""

    label: str
    count: int


@dataclass
class Order:
    customer_id: str
    event_date: date
    guests: int
    delivery_address: str
    items: list[OrderItem] = field(default_factory=list)
    notes: list[GuestGroupNote] = field(default_factory=list)
    status: OrderStatus = OrderStatus.SUBMITTED
    payment_status: PaymentStatus = PaymentStatus.NOT_PAID
    created_at: datetime = field(default_factory=lambda: datetime.now().replace(microsecond=0))
    order_no: str | None = None

    # ---- calculated values -------------------------------------------------
    @property
    def total(self) -> int:
        """DR-3: sum of quantity × unit price, never typed in."""
        return sum(item.line_total for item in self.items)

    @property
    def is_final(self) -> bool:
        return not ALLOWED_TRANSITIONS[self.status]

    def allowed_next_statuses(self) -> list[OrderStatus]:
        return [s for s in OrderStatus if s in ALLOWED_TRANSITIONS[self.status]]

    # ---- behaviour ---------------------------------------------------------
    def change_status(self, new_status: OrderStatus) -> None:
        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise InvalidTransition(
                f"An order cannot go from {self.status.label.lower()} to {new_status.label.lower()}."
            )
        self.status = new_status

    def set_payment_status(self, payment_status: PaymentStatus) -> None:
        """FR-A3.4: set by hand; the system takes no payments."""
        self.payment_status = payment_status

    def validate(self, today: date | None = None) -> None:
        errors = []
        errors += check_event_date(self.event_date, today)
        errors += check_guests(self.guests)
        if not self.delivery_address or not self.delivery_address.strip():
            errors.append("Delivery address is required.")
        if not self.items:
            errors.append("The order has no items.")
        noted = 0
        for note in self.notes:
            if not note.label.strip():
                errors.append("Each allergy or dietary note needs a description.")
            if note.count < 1:
                errors.append("Each allergy or dietary note needs a number of guests of at least 1.")
            noted += max(note.count, 0)
        if self.guests >= 1 and noted > self.guests:
            errors.append("The notes cover more guests than the number of guests.")
        if errors:
            raise ValidationError(errors)
