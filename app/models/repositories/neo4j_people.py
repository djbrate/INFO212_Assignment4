"""Neo4j repositories for customers and staff (Customer and Staff nodes, DR-6)."""
from __future__ import annotations

import uuid

from neo4j.exceptions import ConstraintError

from ..customer import Customer
from ..staff import Staff
from ..validation import ValidationError
from .base import CustomerRepository, StaffRepository
from .db import Neo4jDatabase, to_datetime


def _to_customer(node) -> Customer:
    return Customer(
        id=node["id"],
        name=node["name"],
        email=node["email"],
        password_hash=node["password_hash"],
        created_at=to_datetime(node.get("created_at")),
    )


class Neo4jCustomerRepository(CustomerRepository):
    def __init__(self, db: Neo4jDatabase):
        self.db = db

    def get(self, customer_id):
        rows = self.db.run("MATCH (c:Customer {id: $id}) RETURN c", id=customer_id)
        return _to_customer(rows[0]["c"]) if rows else None

    def get_by_email(self, email):
        rows = self.db.run("MATCH (c:Customer {email: $email}) RETURN c", email=(email or "").strip().lower())
        return _to_customer(rows[0]["c"]) if rows else None

    def save(self, customer):
        customer.id = customer.id or uuid.uuid4().hex
        try:
            self.db.run(
                """
                MERGE (c:Customer {id: $id})
                SET c.name = $name, c.email = $email, c.password_hash = $password_hash,
                    c.created_at = $created_at
                """,
                id=customer.id,
                name=customer.name,
                email=customer.email,
                password_hash=customer.password_hash,
                created_at=customer.created_at,
            )
        except ConstraintError:
            raise ValidationError("An account with this e-mail already exists.")
        return customer


class Neo4jStaffRepository(StaffRepository):
    def __init__(self, db: Neo4jDatabase):
        self.db = db

    def list_all(self):
        rows = self.db.run("MATCH (s:Staff) RETURN s ORDER BY s.name")
        return [Staff(**row["s"]) for row in rows]

    def get(self, staff_id):
        rows = self.db.run("MATCH (s:Staff {id: $id}) RETURN s", id=staff_id)
        return Staff(**rows[0]["s"]) if rows else None

    def save(self, staff):
        staff.id = staff.id or uuid.uuid4().hex
        self.db.run(
            "MERGE (s:Staff {id: $id}) SET s.name = $name, s.email = $email",
            id=staff.id,
            name=staff.name,
            email=staff.email,
        )
        return staff
