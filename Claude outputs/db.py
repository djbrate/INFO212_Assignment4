"""Neo4j connection and schema (CLAUDE.md, HOW: Data storage; requirements NFR-3, DR-4, DR-6).

Only the model/data-access layer imports this module.
"""
from __future__ import annotations

from datetime import date, datetime

from neo4j import GraphDatabase

SCHEMA = [
    "CREATE CONSTRAINT order_no_unique IF NOT EXISTS FOR (o:Order) REQUIRE o.order_no IS UNIQUE",  # DR-4
    "CREATE CONSTRAINT customer_email_unique IF NOT EXISTS FOR (c:Customer) REQUIRE c.email IS UNIQUE",
    "CREATE CONSTRAINT customer_id_unique IF NOT EXISTS FOR (c:Customer) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT staff_id_unique IF NOT EXISTS FOR (s:Staff) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT food_id_unique IF NOT EXISTS FOR (f:FoodItem) REQUIRE f.id IS UNIQUE",
    "CREATE CONSTRAINT category_slug_unique IF NOT EXISTS FOR (e:EventCategory) REQUIRE e.slug IS UNIQUE",
    "CREATE CONSTRAINT question_id_unique IF NOT EXISTS FOR (q:Question) REQUIRE q.id IS UNIQUE",
    "CREATE INDEX order_event_date IF NOT EXISTS FOR (o:Order) ON (o.event_date)",
    "CREATE INDEX order_status IF NOT EXISTS FOR (o:Order) ON (o.status)",
]


class Neo4jDatabase:
    def __init__(self, uri: str, user: str, password: str, database: str | None = None, **driver_options):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), **driver_options)
        self.database = database

    def close(self) -> None:
        self.driver.close()

    def run(self, cypher: str, **params) -> list[dict]:
        """Run a query and return the records as dictionaries."""
        records, _, _ = self.driver.execute_query(cypher, params, database_=self.database)
        return [record.data() for record in records]

    def init_schema(self) -> None:
        for statement in SCHEMA:
            self.run(statement)

    def wipe(self) -> None:
        """Delete every node. Only used by seed.py --reset and the repository tests."""
        self.run("MATCH (n) DETACH DELETE n")


def to_date(value) -> date | None:
    """Convert a neo4j.time.Date (or None) to datetime.date."""
    if value is None:
        return None
    return value.to_native() if hasattr(value, "to_native") else value


def to_datetime(value) -> datetime | None:
    if value is None:
        return None
    return value.to_native() if hasattr(value, "to_native") else value
