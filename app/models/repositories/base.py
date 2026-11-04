"""Repository interfaces.

Controllers talk only to these interfaces. There are two implementations:
`neo4j_*.py` (the real storage layer, NFR-3) and `fake.py` (in memory, for tests).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from ..customer import Customer
from ..enums import OrderStatus
from ..event_category import EventCategory
from ..food_item import FoodItem
from ..order import Order
from ..question import Answer, Question
from ..staff import Staff


class CategoryRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[EventCategory]: ...

    @abstractmethod
    def get(self, slug: str) -> EventCategory | None: ...

    @abstractmethod
    def save(self, category: EventCategory) -> EventCategory: ...


class FoodItemRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[FoodItem]: ...

    @abstractmethod
    def list_published(self) -> list[FoodItem]: ...

    @abstractmethod
    def get(self, item_id: str) -> FoodItem | None: ...

    @abstractmethod
    def save(self, item: FoodItem) -> FoodItem:
        """Create (assigns an id) or update."""

    @abstractmethod
    def delete(self, item_id: str) -> None: ...


class CustomerRepository(ABC):
    @abstractmethod
    def get(self, customer_id: str) -> Customer | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Customer | None: ...

    @abstractmethod
    def save(self, customer: Customer) -> Customer:
        """Create or update. Raises ValidationError if the e-mail is already registered."""


class StaffRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Staff]: ...

    @abstractmethod
    def get(self, staff_id: str) -> Staff | None: ...

    @abstractmethod
    def save(self, staff: Staff) -> Staff: ...

    def get_default(self) -> Staff:
        """The staff member used for answers while the admin panel has no login (FR-A0.1)."""
        staff = self.list_all()
        if staff:
            return staff[0]
        return self.save(Staff(name="Ekte Mat staff", email="staff@ektemat.example"))


class OrderRepository(ABC):
    @abstractmethod
    def next_order_no(self) -> str:
        """A new unique order number (DR-4)."""

    @abstractmethod
    def save(self, order: Order) -> Order:
        """Create (assigns order_no if missing) or update."""

    @abstractmethod
    def get(self, order_no: str) -> Order | None: ...

    @abstractmethod
    def list_for_customer(self, customer_id: str) -> list[Order]: ...

    @abstractmethod
    def list_all(
        self,
        status: OrderStatus | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[Order]:
        """All orders sorted by event date, optionally filtered (FR-A3.1)."""


class QuestionRepository(ABC):
    @abstractmethod
    def save(self, question: Question) -> Question: ...

    @abstractmethod
    def get(self, question_id: str) -> Question | None: ...

    @abstractmethod
    def add_answer(self, question_id: str, answer: Answer) -> Question: ...

    @abstractmethod
    def list_for_order(self, order_no: str) -> list[Question]: ...

    @abstractmethod
    def list_all(self, unanswered_only: bool = False) -> list[Question]: ...


@dataclass
class Repositories:
    categories: CategoryRepository
    food_items: FoodItemRepository
    customers: CustomerRepository
    staff: StaffRepository
    orders: OrderRepository
    questions: QuestionRepository


def format_order_no(number: int) -> str:
    return f"EM-{number:05d}"
