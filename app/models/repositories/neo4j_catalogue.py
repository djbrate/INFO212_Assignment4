"""Neo4j repositories for event categories and food items.

Graph (requirements DR-6): (FoodItem)-[:IN_CATEGORY]->(EventCategory)
"""
from __future__ import annotations

import uuid

from ..enums import Allergen, DietaryLabel
from ..event_category import EventCategory
from ..food_item import FoodItem
from .base import CategoryRepository, FoodItemRepository
from .db import Neo4jDatabase


class Neo4jCategoryRepository(CategoryRepository):
    def __init__(self, db: Neo4jDatabase):
        self.db = db

    def list_all(self):
        rows = self.db.run("MATCH (e:EventCategory) RETURN e ORDER BY e.sort_order, e.name")
        return [EventCategory(**row["e"]) for row in rows]

    def get(self, slug):
        rows = self.db.run("MATCH (e:EventCategory {slug: $slug}) RETURN e", slug=slug)
        return EventCategory(**rows[0]["e"]) if rows else None

    def save(self, category):
        self.db.run(
            "MERGE (e:EventCategory {slug: $slug}) SET e.name = $name, e.sort_order = $sort_order",
            slug=category.slug,
            name=category.name,
            sort_order=category.sort_order,
        )
        return category


_FOOD_RETURN = """
OPTIONAL MATCH (f)-[:IN_CATEGORY]->(e:EventCategory)
WITH f, collect(e.slug) AS categories
RETURN f, categories
"""


def _row_to_item(row) -> FoodItem:
    f = row["f"]
    return FoodItem(
        id=f["id"],
        name=f["name"],
        description=f.get("description", ""),
        price_nok=f["price_nok"],
        min_order=f["min_order"],
        categories=sorted(row["categories"]),
        allergens=Allergen.parse_many(f.get("allergens", [])),
        dietary_labels=DietaryLabel.parse_many(f.get("dietary_labels", [])),
        published=f.get("published", False),
        image_path=f.get("image_path"),
    )


class Neo4jFoodItemRepository(FoodItemRepository):
    def __init__(self, db: Neo4jDatabase):
        self.db = db

    def list_all(self):
        rows = self.db.run("MATCH (f:FoodItem)" + _FOOD_RETURN + " ORDER BY toLower(f.name)")
        return [_row_to_item(r) for r in rows]

    def list_published(self):
        rows = self.db.run("MATCH (f:FoodItem {published: true})" + _FOOD_RETURN + " ORDER BY toLower(f.name)")
        return [_row_to_item(r) for r in rows]

    def get(self, item_id):
        rows = self.db.run("MATCH (f:FoodItem {id: $id})" + _FOOD_RETURN, id=item_id)
        return _row_to_item(rows[0]) if rows else None

    def save(self, item):
        item.id = item.id or uuid.uuid4().hex
        self.db.run(
            """
            MERGE (f:FoodItem {id: $id})
            SET f.name = $name, f.description = $description, f.price_nok = $price_nok,
                f.min_order = $min_order, f.allergens = $allergens,
                f.dietary_labels = $dietary_labels, f.published = $published,
                f.image_path = $image_path
            WITH f
            OPTIONAL MATCH (f)-[old:IN_CATEGORY]->()
            DELETE old
            WITH DISTINCT f
            UNWIND $categories AS slug
            MATCH (e:EventCategory {slug: slug})
            MERGE (f)-[:IN_CATEGORY]->(e)
            """,
            id=item.id,
            name=item.name,
            description=item.description,
            price_nok=item.price_nok,
            min_order=item.min_order,
            allergens=[a.value for a in item.allergens],
            dietary_labels=[d.value for d in item.dietary_labels],
            published=item.published,
            image_path=item.image_path,
            categories=list(item.categories),
        )
        return item

    def delete(self, item_id):
        # Order items keep their own name and unit price, so old orders stay readable.
        self.db.run("MATCH (f:FoodItem {id: $id}) DETACH DELETE f", id=item_id)
