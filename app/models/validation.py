"""Shared validation rules for the model layer.

Every rule here comes from docs/requirements.md; the data-quality problems in
inbox/orders_2024_2025_export.xlsx (price 0, negative guests, 5000 guests,
event before order date) are the reason most of them exist.
"""
from __future__ import annotations

from datetime import date

MAX_GUESTS = 1000  # FR-C3.4 ("a sensible upper limit, e.g. 1000")


class ValidationError(ValueError):
    """Raised when user input breaks a domain rule. Holds one or more messages."""

    def __init__(self, errors):
        if isinstance(errors, str):
            errors = [errors]
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def parse_int(value, field: str) -> int:
    """Parse a whole number from a form value (FR-C2.4: whole numbers only)."""
    try:
        text = str(value).strip()
        number = int(text)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a whole number.")
    return number


def check_price(price_nok) -> list[str]:
    """FR-A1.5: price must be greater than 0 NOK."""
    if not isinstance(price_nok, int) or isinstance(price_nok, bool):
        return ["Price must be a whole number of NOK."]
    return [] if price_nok > 0 else ["Price must be greater than 0 NOK."]


def check_min_order(min_order) -> list[str]:
    """FR-A1.5: minimum order must be at least 1."""
    if not isinstance(min_order, int) or isinstance(min_order, bool):
        return ["Minimum order must be a whole number."]
    return [] if min_order >= 1 else ["Minimum order must be at least 1."]


def check_quantity(quantity: int, min_order: int, item_name: str) -> list[str]:
    """FR-C2.3 and FR-C2.4: whole number > 0 and not below the item's minimum order."""
    if quantity <= 0:
        return ["Quantity must be greater than 0."]
    if quantity < min_order:
        return [f"The minimum order for {item_name} is {min_order}."]
    return []


def check_event_date(event_date: date | None, today: date | None = None) -> list[str]:
    """FR-C3.4: the event date must be in the future."""
    today = today or date.today()
    if event_date is None:
        return ["Event date is required (YYYY-MM-DD)."]
    if event_date <= today:
        return ["Event date must be in the future."]
    return []


def check_guests(guests: int) -> list[str]:
    """FR-C3.4: number of guests between 1 and MAX_GUESTS."""
    if guests < 1 or guests > MAX_GUESTS:
        return [f"Number of guests must be between 1 and {MAX_GUESTS}."]
    return []


def parse_iso_date(value) -> date | None:
    """Parse YYYY-MM-DD (NFR-12). Returns None for empty or invalid input."""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        return None
