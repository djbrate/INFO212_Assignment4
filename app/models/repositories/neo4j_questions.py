"""Neo4j repository for questions and answers (requirements DR-6; FR-A4.x, FR-C5.x).

Graph:
  (Customer)-[:ASKED]->(Question)-[:ABOUT]->(Order)
  (Staff)-[:WROTE]->(Answer)-[:ANSWERS]->(Question)
"""
from __future__ import annotations

import uuid

from ..question import Answer, Question
from .base import QuestionRepository
from .db import Neo4jDatabase, to_datetime

_Q_RETURN = """
MATCH (c:Customer)-[:ASKED]->(q)-[:ABOUT]->(o:Order)
OPTIONAL MATCH (s:Staff)-[:WROTE]->(a:Answer)-[:ANSWERS]->(q)
RETURN q, c.id AS customer_id, o.order_no AS order_no, a, s.id AS staff_id
"""


def _row_to_question(row) -> Question:
    q, a = row["q"], row["a"]
    answer = None
    if a is not None:
        answer = Answer(id=a["id"], text=a["text"], staff_id=row["staff_id"], created_at=to_datetime(a["created_at"]))
    return Question(
        id=q["id"],
        order_no=row["order_no"],
        customer_id=row["customer_id"],
        text=q["text"],
        created_at=to_datetime(q["created_at"]),
        answer=answer,
    )


class Neo4jQuestionRepository(QuestionRepository):
    def __init__(self, db: Neo4jDatabase):
        self.db = db

    def save(self, question):
        question.id = question.id or uuid.uuid4().hex
        self.db.run(
            """
            MATCH (c:Customer {id: $customer_id}), (o:Order {order_no: $order_no})
            MERGE (q:Question {id: $id})
            SET q.text = $text, q.created_at = $created_at
            MERGE (c)-[:ASKED]->(q)
            MERGE (q)-[:ABOUT]->(o)
            """,
            id=question.id,
            customer_id=question.customer_id,
            order_no=question.order_no,
            text=question.text,
            created_at=question.created_at,
        )
        return question

    def get(self, question_id):
        rows = self.db.run("MATCH (q:Question {id: $id})" + _Q_RETURN, id=question_id)
        return _row_to_question(rows[0]) if rows else None

    def add_answer(self, question_id, answer):
        answer.id = answer.id or uuid.uuid4().hex
        self.db.run(
            """
            MATCH (q:Question {id: $question_id}), (s:Staff {id: $staff_id})
            OPTIONAL MATCH (old:Answer)-[:ANSWERS]->(q)
            DETACH DELETE old
            WITH q, s
            CREATE (s)-[:WROTE]->(:Answer {id: $id, text: $text, created_at: $created_at})-[:ANSWERS]->(q)
            """,
            question_id=question_id,
            staff_id=answer.staff_id,
            id=answer.id,
            text=answer.text,
            created_at=answer.created_at,
        )
        return self.get(question_id)

    def list_for_order(self, order_no):
        rows = self.db.run(
            "MATCH (q:Question)-[:ABOUT]->(:Order {order_no: $order_no})" + _Q_RETURN + " ORDER BY q.created_at",
            order_no=order_no,
        )
        return [_row_to_question(r) for r in rows]

    def list_all(self, unanswered_only=False):
        where = " WHERE NOT EXISTS { (:Answer)-[:ANSWERS]->(q) }" if unanswered_only else ""
        rows = self.db.run("MATCH (q:Question)" + where + _Q_RETURN + " ORDER BY q.created_at DESC")
        return [_row_to_question(r) for r in rows]
