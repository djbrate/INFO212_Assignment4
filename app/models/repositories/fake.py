"""In-memory repositories for fast tests (implementation plan, "Tests").

They behave like the Neo4j repositories but keep data in dictionaries. Like the
Neo4j versions, save() sets the new id on the object passed in. Stored objects are
copied in and out so tests cannot change stored data by accident.
"""
from __future__ import annotations

import copy
import uuid
from datetime import date

from ..customer import Customer
from ..enums import OrderStatus
from ..event_category import EventCategory
from ..food_item import FoodItem
from ..order import Order
from ..question import Answer, Question
from ..staff import Staff
from ..validation import ValidationError
from .base import (
    CategoryRepository,
    CustomerRepository,
    FoodItemRepository,
    OrderRepository,
    QuestionRepository,
    Repositories,
    StaffRepository,
    format_order_no,
)


def _new_id() -> str:
    return uuid.uuid4().hex


class FakeCategoryRepository(CategoryRepository):
    def __init__(self):
        self._data: dict[str, EventCategory] = {}

    def list_all(self):
        return sorted((copy.deepcopy(c) for c in self._data.values()), key=lambda c: (c.sort_order, c.name))

    def get(self, slug):
        return copy.deepcopy(self._data.get(slug))

    def save(self, category):
        self._data[category.slug] = copy.deepcopy(category)
        return copy.deepcopy(category)


class FakeFoodItemRepository(FoodItemRepository):
    def __init__(self):
        self._data: dict[str, FoodItem] = {}

    def list_all(self):
        return sorted((copy.deepcopy(i) for i in self._data.values()), key=lambda i: i.name.lower())

    def list_published(self):
        return [i for i in self.list_all() if i.published]

    def get(self, item_id):
        return copy.deepcopy(self._data.get(item_id))

    def save(self, item):
        item.id = item.id or _new_id()  # like Neo4j: the caller's object gets the id
        self._data[item.id] = copy.deepcopy(item)
        return copy.deepcopy(item)

    def delete(self, item_id):
        self._data.pop(item_id, None)


class FakeCustomerRepository(CustomerRepository):
    def __init__(self):
        self._data: dict[str, Customer] = {}

    def get(self, customer_id):
        return copy.deepcopy(self._data.get(customer_id))

    def get_by_email(self, email):
        email = (email or "").strip().lower()
        for c in self._data.values():
            if c.email == email:
                return copy.deepcopy(c)
        return None

    def save(self, customer):
        existing = self.get_by_email(customer.email)
        if existing and existing.id != customer.id:
            raise ValidationError("An account with this e-mail already exists.")
        customer.id = customer.id or _new_id()
        self._data[customer.id] = copy.deepcopy(customer)
        return copy.deepcopy(customer)


class FakeStaffRepository(StaffRepository):
    def __init__(self):
        self._data: dict[str, Staff] = {}

    def list_all(self):
        return sorted((copy.deepcopy(s) for s in self._data.values()), key=lambda s: s.name)

    def get(self, staff_id):
        return copy.deepcopy(self._data.get(staff_id))

    def save(self, staff):
        staff.id = staff.id or _new_id()
        self._data[staff.id] = copy.deepcopy(staff)
        return copy.deepcopy(staff)


class FakeOrderRepository(OrderRepository):
    def __init__(self):
        self._data: dict[str, Order] = {}
        self._counter = 0

    def next_order_no(self):
        self._counter += 1
        return format_order_no(self._counter)

    def save(self, order):
        order.order_no = order.order_no or self.next_order_no()
        self._data[order.order_no] = copy.deepcopy(order)
        return copy.deepcopy(order)

    def get(self, order_no):
        return copy.deepcopy(self._data.get(order_no))

    def list_for_customer(self, customer_id):
        orders = [copy.deepcopy(o) for o in self._data.values() if o.customer_id == customer_id]
        return sorted(orders, key=lambda o: o.created_at, reverse=True)

    def list_all(self, status: OrderStatus | None = None, date_from: date | None = None, date_to: date | None = None):
        result = []
        for o in self._data.values():
            if status and o.status != status:
                continue
            if date_from and o.event_date < date_from:
                continue
            if date_to and o.event_date > date_to:
                continue
            result.append(copy.deepcopy(o))
        return sorted(result, key=lambda o: (o.event_date, o.order_no))


class FakeQuestionRepository(QuestionRepository):
    def __init__(self):
        self._data: dict[str, Question] = {}

    def save(self, question):
        question.id = question.id or _new_id()
        self._data[question.id] = copy.deepcopy(question)
        return copy.deepcopy(question)

    def get(self, question_id):
        return copy.deepcopy(self._data.get(question_id))

    def add_answer(self, question_id, answer: Answer):
        question = self._data[question_id]
        answer.id = answer.id or _new_id()
        question.answer = copy.deepcopy(answer)
        return copy.deepcopy(question)

    def list_for_order(self, order_no):
        return sorted(
            (copy.deepcopy(q) for q in self._data.values() if q.order_no == order_no), key=lambda q: q.created_at
        )

    def list_all(self, unanswered_only=False):
        qs = [copy.deepcopy(q) for q in self._data.values() if not (unanswered_only and q.is_answered)]
        return sorted(qs, key=lambda q: q.created_at, reverse=True)


def make_fake_repositories() -> Repositories:
    return Repositories(
        categories=FakeCategoryRepository(),
        food_items=FakeFoodItemRepository(),
        customers=FakeCustomerRepository(),
        staff=FakeStaffRepository(),
        orders=FakeOrderRepository(),
        questions=FakeQuestionRepository(),
    )
