"""Repository tests against a real Neo4j (graph model DR-6, unique order numbers DR-4).

Run with:  docker compose up -d   then   pytest -m neo4j
Skipped automatically when Neo4j is not reachable. WARNING: wipes the configured database.
"""
from datetime import date, timedelta

import pytest

from app.models.customer import Customer
from app.models.enums import Allergen, DietaryLabel, OrderStatus, PaymentStatus
from app.models.event_category import DEFAULT_CATEGORIES
from app.models.food_item import FoodItem
from app.models.order import GuestGroupNote, Order, OrderItem
from app.models.question import Answer, Question
from app.models.repositories import make_neo4j_repositories
from app.models.staff import Staff
from app.models.validation import ValidationError

pytestmark = pytest.mark.neo4j


@pytest.fixture
def repos(neo4j_db):
    r = make_neo4j_repositories(neo4j_db)
    for c in DEFAULT_CATEGORIES:
        r.categories.save(c)
    return r


def test_food_item_round_trip(repos):
    item = repos.food_items.save(FoodItem(
        name="Fish soup", description="Cod", price_nok=189, min_order=10, categories=["conference", "corporate-lunch"],
        allergens=[Allergen.FISH], dietary_labels=[DietaryLabel.LACTOSE_FREE], published=True))
    got = repos.food_items.get(item.id)
    assert got == item
    got.categories = ["wedding"]
    got.published = False
    repos.food_items.save(got)
    assert repos.food_items.get(item.id).categories == ["wedding"]
    assert repos.food_items.list_published() == []
    repos.food_items.delete(item.id)
    assert repos.food_items.get(item.id) is None


def test_customer_email_is_unique(repos):
    repos.customers.save(Customer.register("Kari", "kari@example.com", "long-password"))
    assert repos.customers.get_by_email("KARI@example.com").name == "Kari"
    with pytest.raises(ValidationError):
        repos.customers.save(Customer.register("Kari 2", "kari@example.com", "long-password"))


def test_order_graph_round_trip_and_filters(repos, neo4j_db):
    customer = repos.customers.save(Customer.register("Kari", "kari@example.com", "long-password"))
    soup = repos.food_items.save(FoodItem(name="Fish soup", description="", price_nok=189, min_order=1, published=True))
    order = repos.orders.save(Order(
        customer_id=customer.id, event_date=date.today() + timedelta(days=7), guests=20, delivery_address="Bryggen 1",
        items=[OrderItem(soup.id, soup.name, 20, 189)], notes=[GuestGroupNote("vegan", 3), GuestGroupNote("halal", 1)]))
    assert order.order_no == "EM-00001"

    got = repos.orders.get(order.order_no)
    assert got.total == 20 * 189 and got.customer_id == customer.id
    assert [(n.label, n.count) for n in got.notes] == [("vegan", 3), ("halal", 1)]
    assert got.event_date == order.event_date

    got.change_status(OrderStatus.APPROVED)
    got.set_payment_status(PaymentStatus.DEPOSIT_PAID)
    repos.orders.save(got)
    again = repos.orders.get(order.order_no)
    assert (again.status, again.payment_status) == (OrderStatus.APPROVED, PaymentStatus.DEPOSIT_PAID)
    assert len(again.items) == 1  # saving twice does not duplicate items

    assert [o.order_no for o in repos.orders.list_all(status=OrderStatus.APPROVED)] == [order.order_no]
    assert repos.orders.list_all(status=OrderStatus.SUBMITTED) == []
    assert repos.orders.list_all(date_from=date.today() + timedelta(days=8)) == []
    assert [o.order_no for o in repos.orders.list_for_customer(customer.id)] == [order.order_no]

    # The graph follows DR-6
    path = neo4j_db.run(
        "MATCH (:Customer)-[:PLACED]->(o:Order)-[:HAS_ITEM]->(:OrderItem)-[:OF]->(:FoodItem) RETURN count(o) AS n")
    assert path[0]["n"] == 1


def test_order_numbers_are_unique(repos):
    numbers = {repos.orders.next_order_no() for _ in range(5)}
    assert len(numbers) == 5


def test_question_and_answer_graph(repos, neo4j_db):
    customer = repos.customers.save(Customer.register("Kari", "kari@example.com", "long-password"))
    staff = repos.staff.save(Staff(name="Admin", email="admin@ektemat.example"))
    soup = repos.food_items.save(FoodItem(name="Fish soup", description="", price_nok=189, min_order=1, published=True))
    order = repos.orders.save(Order(customer_id=customer.id, event_date=date.today() + timedelta(days=7), guests=5,
                                    delivery_address="Bryggen 1", items=[OrderItem(soup.id, soup.name, 5, 189)]))
    q = repos.questions.save(Question.ask(order.order_no, customer.id, "Gluten-free bread?"))
    assert [x.id for x in repos.questions.list_all(unanswered_only=True)] == [q.id]

    answered = repos.questions.add_answer(q.id, Answer.write("Yes.", staff.id))
    assert answered.answer.text == "Yes." and answered.answer.staff_id == staff.id
    assert repos.questions.list_all(unanswered_only=True) == []
    assert repos.questions.list_for_order(order.order_no)[0].is_answered

    rows = neo4j_db.run("MATCH (:Staff)-[:WROTE]->(:Answer)-[:ANSWERS]->(:Question)-[:ABOUT]->(:Order) "
                        "RETURN count(*) AS n")
    assert rows[0]["n"] == 1


def test_seed_runs_against_neo4j(repos, tmp_path):
    from app.models.services.image_service import ImageService, StubImageProvider
    from seed import seed

    seed(repos, ImageService(str(tmp_path), StubImageProvider()))
    assert len(repos.food_items.list_published()) == 10
    assert len(repos.orders.list_all()) == 3
    assert len(repos.questions.list_all(unanswered_only=True)) == 1
