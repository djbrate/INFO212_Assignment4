"""Shopping cart kept in the Flask session (CLAUDE.md, Customer Site 2;
requirements FR-C2.1–2.4; implementation plan decision "Cart: Flask session").

The cart is plain Python: it stores {food_item_id: quantity} and is turned into
order items only when the customer submits the order.
"""
from __future__ import annotations

from dataclasses import dataclass

from .food_item import FoodItem
from .order import OrderItem
from .validation import ValidationError, check_quantity, parse_int

SESSION_KEY = "cart"


@dataclass
class CartLine:
    item: FoodItem
    quantity: int

    @property
    def line_total(self) -> int:
        return self.quantity * self.item.price_nok


class Cart:
    def __init__(self, contents: dict[str, int] | None = None):
        self._contents: dict[str, int] = dict(contents or {})

    # ---- session helpers ---------------------------------------------------
    @classmethod
    def from_session(cls, session) -> "Cart":
        return cls(session.get(SESSION_KEY, {}))

    def save(self, session) -> None:
        session[SESSION_KEY] = dict(self._contents)

    # ---- changes -----------------------------------------------------------
    def set(self, item: FoodItem, raw_quantity) -> None:
        """Add or change an item. Rejects quantities below the item's minimum (FR-C2.3)."""
        if not item.published:
            raise ValidationError("This item is not available.")
        quantity = parse_int(raw_quantity, "Quantity")
        errors = check_quantity(quantity, item.min_order, item.name)
        if errors:
            raise ValidationError(errors)
        self._contents[item.id] = quantity

    def remove(self, item_id: str) -> None:
        self._contents.pop(item_id, None)

    def clear(self) -> None:
        self._contents.clear()

    # ---- reading -----------------------------------------------------------
    def quantity_of(self, item_id: str) -> int:
        return self._contents.get(item_id, 0)

    @property
    def count(self) -> int:
        return len(self._contents)

    def is_empty(self) -> bool:
        return not self._contents

    def lines(self, food_repo) -> list[CartLine]:
        """Resolve item ids against the repository; silently drops items that no longer exist."""
        lines = []
        for item_id, quantity in self._contents.items():
            item = food_repo.get(item_id)
            if item is not None and item.published:
                lines.append(CartLine(item, quantity))
        return lines

    def total(self, food_repo) -> int:
        """FR-C2.2: estimated total in NOK."""
        return sum(line.line_total for line in self.lines(food_repo))

    def to_order_items(self, food_repo) -> list[OrderItem]:
        return [
            OrderItem(food_item_id=l.item.id, name=l.item.name, quantity=l.quantity, unit_price=l.item.price_nok)
            for l in self.lines(food_repo)
        ]
