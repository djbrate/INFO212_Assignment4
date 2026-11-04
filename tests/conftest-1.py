"""Shared test fixtures (implementation plan, "Tests").

Most tests use the in-memory fake repositories, so they run without Neo4j.
Tests marked `neo4j` use a real database and are skipped when it is not running.
"""
from __future__ import annotations

import os
from datetime import date, timedelta

import pytest

from app import create_app
from app.config import TestConfig
from app.models.customer import Customer
from app.models.enums import Allergen
from app.models.event_category import DEFAULT_CATEGORIES
from app.models.food_item import FoodItem
from app.models.repositories.fake import make_fake_repositories

PASSWORD = "secret-pass-1"


@pytest.fixture
def repos():
    r = make_fake_repositories()
    for c in DEFAULT_CATEGORIES:
        r.categories.save(c)
    return r


@pytest.fixture
def app(repos, tmp_path):
    class Cfg(TestConfig):
        UPLOAD_FOLDER = str(tmp_path / "uploads")

    return create_app(Cfg, repositories=repos)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def soup(repos):
    return repos.food_items.save(FoodItem(
        name="Fish soup", description="Bergen cod", price_nok=189, min_order=10,
        categories=["corporate-lunch"], allergens=[Allergen.FISH, Allergen.MILK], published=True))


@pytest.fixture
def hidden_item(repos):
    return repos.food_items.save(FoodItem(
        name="Secret test dish", description="", price_nok=100, min_order=1,
        categories=["wedding"], published=False))


def make_customer(repos, email="kari@example.com", name="Kari"):
    return repos.customers.save(Customer.register(name, email, PASSWORD))


def login(client, email="kari@example.com"):
    return client.post("/login", data={"email": email, "password": PASSWORD})


@pytest.fixture
def customer(repos):
    return make_customer(repos)


@pytest.fixture
def future_date():
    return (date.today() + timedelta(days=14)).isoformat()


# ---- real Neo4j ---------------------------------------------------------------
@pytest.fixture
def neo4j_db():
    """A real Neo4j database, wiped before the test. Skips if Neo4j is not reachable.

    Uses NEO4J_TEST_URI / NEO4J_TEST_USER / NEO4J_TEST_PASSWORD, falling back to the
    normal NEO4J_* settings from .env. WARNING: the test wipes that database.
    """
    from dotenv import load_dotenv

    try:
        from neo4j import GraphDatabase  # noqa: F401
    except ImportError:
        try:
            import neo4j
            where = list(getattr(neo4j, "__path__", [])) or getattr(neo4j, "__file__", "?")
        except ImportError:
            where = "nothing"
        pytest.fail(
            "The neo4j Python driver is not installed for this Python "
            f"(found only {where}). Run: python -m pip install -r requirements.txt, "
            "then: python -m pytest -m neo4j",
            pytrace=False,
        )
    from app.models.repositories.db import Neo4jDatabase

    load_dotenv()
    uri = os.environ.get("NEO4J_TEST_URI", os.environ.get("NEO4J_URI", "bolt://localhost:7687"))
    user = os.environ.get("NEO4J_TEST_USER", os.environ.get("NEO4J_USER", "neo4j"))
    password = os.environ.get("NEO4J_TEST_PASSWORD", os.environ.get("NEO4J_PASSWORD", ""))
    # Short timeouts: give up after a few seconds instead of 60 s per test when Neo4j is down.
    db = Neo4jDatabase(uri, user, password, connection_timeout=5, connection_acquisition_timeout=8)
    try:
        db.driver.verify_connectivity()
    except Exception as exc:
        db.close()
        pytest.skip(f"Neo4j not available at {uri} (check: docker compose ps / docker compose logs neo4j): {exc}")
    db.wipe()
    db.init_schema()
    yield db
    db.wipe()
    db.close()
