"""Seed script – synthetic data only (CLAUDE.md, Running it; requirements NFR-6).

Creates the event categories, sample food items with placeholder pictures,
one admin (Staff), two test customers, a few orders and a question.

    python seed.py           # add the sample data (skips anything that already exists)
    python seed.py --reset   # DELETE everything in the Neo4j database first, then seed

Dishes and prices come from inbox/lunch menu autumn.txt and docs/requirements.md
section 5 (inbox/orders_2024_2025_export.xlsx). Allergens per dish, minimum
orders and descriptions are synthetic sample values.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta

from app.models.customer import Customer
from app.models.enums import Allergen as A
from app.models.enums import DietaryLabel as D
from app.models.enums import OrderStatus, PaymentStatus
from app.models.event_category import DEFAULT_CATEGORIES
from app.models.food_item import FoodItem
from app.models.order import GuestGroupNote, Order, OrderItem
from app.models.question import Answer, Question
from app.models.repositories.base import Repositories
from app.models.services.image_service import ImageService
from app.models.staff import Staff

# Test logins (synthetic). Printed at the end of the seed run and listed in README.MD.
TEST_CUSTOMERS = [
    ("Kari Nordmann", "kari@example.com", "ektemat-test-1"),
    ("Fjordtek AS (test)", "lunch@fjordtek.example", "ektemat-test-2"),
]
ADMIN = ("Ekte Mat admin", "admin@ektemat.example")

FOOD_ITEMS = [
    # name, description, price NOK, min order, categories, allergens, dietary labels
    ("Fish soup with Bergen cod", "Creamy fish soup with root vegetables and sourdough bread.", 189, 10,
     ["corporate-lunch", "conference", "private-party"], [A.FISH, A.MILK, A.GLUTEN, A.CELERY], []),
    ("Slow-cooked lamb from Voss", "Lamb shoulder with barley risotto.", 245, 10,
     ["corporate-lunch", "private-party", "birthday"], [A.CELERY, A.MILK], []),
    ("Beetroot and chickpea salad", "With goat cheese from Hardanger.", 165, 8,
     ["corporate-lunch", "conference", "birthday"], [A.MILK, A.MUSTARD], [D.VEGETARIAN, D.GLUTEN_FREE]),
    ("Rakfisk tasting (November only)", "Seasonal fermented trout with lefse and sour cream.", 210, 10,
     ["christmas-party", "other"], [A.FISH, A.MILK, A.GLUTEN], []),
    ("Seasonal lunch buffet", "Bread, salads, a warm dish and something sweet.", 229, 15,
     ["corporate-lunch", "conference"], [A.GLUTEN, A.MILK], []),
    ("Meeting sandwiches", "Open sandwiches with seasonal toppings.", 129, 10,
     ["conference", "corporate-lunch", "birthday"], [A.GLUTEN, A.MILK, A.MUSTARD], []),
    ("Confirmation buffet", "Traditional buffet for confirmation celebrations.", 395, 20,
     ["confirmation", "private-party"], [A.GLUTEN, A.MILK, A.FISH], []),
    ("Wedding served dinner (3 courses)", "Starter, main course and dessert, served at the table.", 875, 30,
     ["wedding"], [A.MILK, A.GLUTEN, A.CELERY], []),
    ("Traditional julebord buffet", "Ribbe, pinnekjøtt and Christmas sides.", 595, 20,
     ["christmas-party"], [A.GLUTEN, A.MILK, A.MUSTARD, A.CELERY], []),
    ("Vegan root vegetable stew", "Hearty stew with lentils and herbs (synthetic sample dish).", 175, 8,
     ["corporate-lunch", "conference", "private-party", "birthday", "other"], [A.CELERY], [D.VEGAN, D.GLUTEN_FREE]),
]


def seed(repos: Repositories, images: ImageService | None = None, today: date | None = None) -> dict:
    """Fill the repositories with sample data. Works with Neo4j and with the fake repositories."""
    today = today or date.today()
    for category in DEFAULT_CATEGORIES:
        repos.categories.save(category)

    admin = next((s for s in repos.staff.list_all() if s.email == ADMIN[1]), None)
    admin = admin or repos.staff.save(Staff(name=ADMIN[0], email=ADMIN[1]))

    customers = []
    for name, email, password in TEST_CUSTOMERS:
        existing = repos.customers.get_by_email(email)
        customers.append(existing or repos.customers.save(Customer.register(name, email, password)))

    existing_names = {i.name for i in repos.food_items.list_all()}
    items = {i.name: i for i in repos.food_items.list_all()}
    for name, desc, price, min_order, cats, allergens, diets in FOOD_ITEMS:
        if name in existing_names:
            continue
        item = FoodItem(name=name, description=desc, price_nok=price, min_order=min_order, categories=cats,
                        allergens=allergens, dietary_labels=diets, published=True)
        item.validate()
        item = repos.food_items.save(item)
        if images is not None:
            token = images.pending_from_instruction(name)
            item.image_path = images.confirm(token, item.id)
            item = repos.food_items.save(item)
        items[name] = item

    created_orders = []
    if not repos.orders.list_all():
        kari, fjordtek = customers

        def line(name, qty):
            i = items[name]
            return OrderItem(food_item_id=i.id, name=i.name, quantity=qty, unit_price=i.price_nok)

        o1 = Order(customer_id=fjordtek.id, event_date=today + timedelta(days=9), guests=40,
                   delivery_address="Strandkaien 2, 5013 Bergen",
                   items=[line("Seasonal lunch buffet", 40)],
                   notes=[GuestGroupNote("vegan", 4), GuestGroupNote("nut allergy", 2)])
        o2 = Order(customer_id=kari.id, event_date=today + timedelta(days=30), guests=60,
                   delivery_address="Fjellveien 10, 5019 Bergen",
                   items=[line("Confirmation buffet", 55), line("Vegan root vegetable stew", 8)],
                   notes=[GuestGroupNote("gluten-free", 3)])
        o3 = Order(customer_id=fjordtek.id, event_date=today + timedelta(days=45), guests=80,
                   delivery_address="Strandkaien 2, 5013 Bergen",
                   items=[line("Traditional julebord buffet", 80)],
                   notes=[GuestGroupNote("halal", 5), GuestGroupNote("shellfish allergy", 1)])
        for order in (o1, o2, o3):
            order.validate(today)
        o1.change_status(OrderStatus.APPROVED)
        o1.set_payment_status(PaymentStatus.INVOICED)
        created_orders = [repos.orders.save(o) for o in (o1, o2, o3)]

        q1 = repos.questions.save(Question.ask(o1.order_no, fjordtek.id, "Can you deliver at 11:30 instead of 12:00?"))
        repos.questions.add_answer(q1.id, Answer.write("Yes, 11:30 is fine. See you then!", admin.id))
        repos.questions.save(Question.ask(o2.order_no, kari.id, "Is the confirmation buffet suitable for children?"))

    return {"customers": customers, "admin": admin, "items": items, "orders": created_orders}


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Ekte Mat Online with synthetic data.")
    parser.add_argument("--reset", action="store_true", help="delete ALL data in the Neo4j database first")
    args = parser.parse_args()

    from app import create_app

    app = create_app()
    with app.app_context():
        db = app.extensions.get("neo4j")
        if db is None:
            print("REPOSITORY is not 'neo4j' – nothing to seed (fake repositories live only in memory).")
            return
        db.init_schema()
        if args.reset:
            db.wipe()
            print("Deleted all existing data.")
        result = seed(app.extensions["repos"], app.extensions["images"])

    print(f"Seeded {len(result['items'])} food items, {len(result['orders'])} new orders.")
    print("Admin panel: http://localhost:5000/admin/  (no login for now, FR-A0.1)")
    print("Test customers (synthetic):")
    for name, email, password in TEST_CUSTOMERS:
        print(f"  {email}  /  {password}")


if __name__ == "__main__":
    main()
