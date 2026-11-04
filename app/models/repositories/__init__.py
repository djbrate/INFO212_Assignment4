"""Data-access layer. The only place that talks to storage (requirements NFR-3)."""
from __future__ import annotations

from .base import Repositories


def make_neo4j_repositories(db) -> Repositories:
    from .neo4j_catalogue import Neo4jCategoryRepository, Neo4jFoodItemRepository
    from .neo4j_orders import Neo4jOrderRepository
    from .neo4j_people import Neo4jCustomerRepository, Neo4jStaffRepository
    from .neo4j_questions import Neo4jQuestionRepository

    return Repositories(
        categories=Neo4jCategoryRepository(db),
        food_items=Neo4jFoodItemRepository(db),
        customers=Neo4jCustomerRepository(db),
        staff=Neo4jStaffRepository(db),
        orders=Neo4jOrderRepository(db),
        questions=Neo4jQuestionRepository(db),
    )
