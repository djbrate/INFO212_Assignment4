"""Food items (CLAUDE.md, Admin panel 1; requirements FR-A1.1–1.5)."""
from __future__ import annotations

from dataclasses import dataclass, field

from .enums import Allergen, DietaryLabel
from .validation import ValidationError, check_min_order, check_price


@dataclass
class FoodItem:
    name: str
    description: str
    price_nok: int
    min_order: int
    categories: list[str] = field(default_factory=list)  # EventCategory slugs
    allergens: list[Allergen] = field(default_factory=list)
    dietary_labels: list[DietaryLabel] = field(default_factory=list)
    published: bool = False
    image_path: str | None = None  # relative to the upload folder
    id: str | None = None

    def validate(self) -> None:
        errors = []
        if not self.name or not self.name.strip():
            errors.append("Name is required.")
        errors += check_price(self.price_nok)
        errors += check_min_order(self.min_order)
        if errors:
            raise ValidationError(errors)
