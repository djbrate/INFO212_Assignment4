"""Neo4j repository for orders (requirements DR-3, DR-4, DR-6; FR-A3.1).

Graph:
  (Customer)-[:PLACED]->(Order)-[:HAS_ITEM]->(OrderItem)-[:OF]->(FoodItem)
  (Order)-[:HAS_NOTE]->(GuestGroupNote)
"""
from __future__ import annotations

from ..enums import OrderStatus, PaymentStatus
from ..order import GuestGroupNote, Order, OrderItem
from .base import OrderRepository, format_order_no
from .db import Neo4jDatabase, to_date, to_datetime

_ORDER_RETURN = """
OPTIONAL MATCH (c:Customer)-[:PLACED]->(o)
OPTIONAL MATCH (o)-[:HAS_ITEM]->(oi:OrderItem)
WITH o, c, collect(oi {.*}) AS items
OPTIONAL MATCH (o)-[:HAS_NOTE]->(n:GuestGroupNote)
WITH o, c, items, collect(n {.*}) AS notes
RETURN o, c.id AS customer_id, items, notes
"""


def _row_to_order(row) -> Order:
    o = row["o"]
    items = sorted(row["items"], key=lambda i: i.get("position", 0))
    notes = sorted(row["notes"], key=lambda n: n.get("position", 0))
    return Order(
        order_no=o["order_no"],
        customer_id=row["customer_id"],
        event_date=to_date(o["event_date"]),
        guests=o["guests"],
        delivery_address=o["delivery_address"],
        status=OrderStatus(o["status"]),
        payment_status=PaymentStatus(o["payment_status"]),
        created_at=to_datetime(o["created_at"]),
        items=[
            OrderItem(food_item_id=i["food_item_id"], name=i["name"], quantity=i["quantity"], unit_price=i["unit_price"])
            for i in items
        ],
        notes=[GuestGroupNote(label=n["label"], count=n["count"]) for n in notes],
    )


class Neo4jOrderRepository(OrderRepository):
    def __init__(self, db: Neo4jDatabase):
        self.db = db

    def next_order_no(self):
        rows = self.db.run(
            "MERGE (c:Counter {name: 'order'}) "
            "SET c.value = coalesce(c.value, 0) + 1 RETURN c.value AS value"
        )
        return format_order_no(rows[0]["value"])

    def save(self, order):
        order.order_no = order.order_no or self.next_order_no()
        self.db.run(
            """
            MATCH (c:Customer {id: $customer_id})
            MERGE (o:Order {order_no: $order_no})
            SET o.event_date = $event_date, o.guests = $guests,
                o.delivery_address = $delivery_address, o.status = $status,
                o.payment_status = $payment_status, o.created_at = $created_at,
                o.total = $total
            MERGE (c)-[:PLACED]->(o)
            WITH o
            OPTIONAL MATCH (o)-[:HAS_ITEM|HAS_NOTE]->(old)
            DETACH DELETE old
            WITH DISTINCT o
            FOREACH (i IN $items |
                CREATE (o)-[:HAS_ITEM]->(:OrderItem {
                    food_item_id: i.food_item_id, name: i.name, quantity: i.quantity,
                    unit_price: i.unit_price, position: i.position}))
            FOREACH (n IN $notes |
                CREATE (o)-[:HAS_NOTE]->(:GuestGroupNote {label: n.label, count: n.count, position: n.position}))
            WITH o
            MATCH (o)-[:HAS_ITEM]->(oi:OrderItem)
            MATCH (f:FoodItem {id: oi.food_item_id})
            MERGE (oi)-[:OF]->(f)
            """,
            customer_id=order.customer_id,
            order_no=order.order_no,
            event_date=order.event_date,
            guests=order.guests,
            delivery_address=order.delivery_address,
            status=order.status.value,
            payment_status=order.payment_status.value,
            created_at=order.created_at,
            total=order.total,  # stored for convenience; always calculated by the model (DR-3)
            items=[
                {"food_item_id": i.food_item_id, "name": i.name, "quantity": i.quantity,
                 "unit_price": i.unit_price, "position": pos}
                for pos, i in enumerate(order.items)
            ],
            notes=[{"label": n.label, "count": n.count, "position": pos} for pos, n in enumerate(order.notes)],
        )
        return order

    def get(self, order_no):
        rows = self.db.run("MATCH (o:Order {order_no: $order_no})" + _ORDER_RETURN, order_no=order_no)
        return _row_to_order(rows[0]) if rows else None

    def list_for_customer(self, customer_id):
        rows = self.db.run(
            "MATCH (:Customer {id: $customer_id})-[:PLACED]->(o:Order)" + _ORDER_RETURN + " ORDER BY o.created_at DESC",
            customer_id=customer_id,
        )
        return [_row_to_order(r) for r in rows]

    def list_all(self, status=None, date_from=None, date_to=None):
        rows = self.db.run(
            """
            MATCH (o:Order)
            WHERE ($status IS NULL OR o.status = $status)
              AND ($date_from IS NULL OR o.event_date >= $date_from)
              AND ($date_to IS NULL OR o.event_date <= $date_to)
            """
            + _ORDER_RETURN
            + " ORDER BY o.event_date, o.order_no",
            status=status.value if status else None,
            date_from=date_from,
            date_to=date_to,
        )
        return [_row_to_order(r) for r in rows]
