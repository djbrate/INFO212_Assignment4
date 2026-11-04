"""Fixed value lists used across the model layer.

Fixed lists instead of free text avoid typos such as "Confimed" and the ten
different spellings of the order channel found in the old Excel export
(docs/requirements.md NFR-11; inbox/orders_2024_2025_export.xlsx).
"""
from enum import Enum


class LabelledEnum(str, Enum):
    """A string enum with a human-readable label for the templates."""

    @property
    def label(self) -> str:
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def choices(cls):
        return [(member.value, member.label) for member in cls]

    @classmethod
    def parse_many(cls, values):
        """Turn a list of raw strings (e.g. from a form) into members, ignoring unknown values."""
        valid = {m.value: m for m in cls}
        return [valid[v] for v in values if v in valid]


class OrderStatus(LabelledEnum):
    """Order status (CLAUDE.md, Admin panel 3; requirements FR-A3.3, DR-1)."""

    SUBMITTED = "submitted"
    APPROVED = "approved"
    IN_PREPARATION = "in_preparation"
    DELIVERED = "delivered"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class PaymentStatus(LabelledEnum):
    """Payment status, set by hand by staff (CLAUDE.md, Admin panel 3; DR-2, FR-A3.4)."""

    NOT_PAID = "not_paid"
    DEPOSIT_PAID = "deposit_paid"
    INVOICED = "invoiced"
    PAID = "paid"


class Allergen(LabelledEnum):
    """Allergens (FR-A1.3; inbox/lunch menu autumn.txt; inbox/customer_emails_export.csv E022)."""

    FISH = "fish"
    MILK = "milk"
    GLUTEN = "gluten"
    NUTS = "nuts"
    CELERY = "celery"
    MUSTARD = "mustard"
    SHELLFISH = "shellfish"


class DietaryLabel(LabelledEnum):
    """Dietary labels (FR-A1.4; inbox/orders_2024_2025_export.xlsx, dietary_notes)."""

    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    GLUTEN_FREE = "gluten_free"
    LACTOSE_FREE = "lactose_free"
    HALAL = "halal"

    @property
    def label(self) -> str:
        return self.value.replace("_", "-").capitalize()
