"""Questions about an order and Ekte Mat's answers.

Sources: CLAUDE.md (Admin panel 4, Customer Site 5); requirements FR-A4.1–4.2,
FR-C5.1–5.2; Question and Answer nodes in DR-6.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .validation import ValidationError

MAX_TEXT_LENGTH = 2000


def _now() -> datetime:
    return datetime.now().replace(microsecond=0)


def _clean_text(text: str, what: str) -> str:
    text = (text or "").strip()
    if not text:
        raise ValidationError(f"The {what} cannot be empty.")
    if len(text) > MAX_TEXT_LENGTH:
        raise ValidationError(f"The {what} can be at most {MAX_TEXT_LENGTH} characters.")
    return text


@dataclass
class Answer:
    text: str
    staff_id: str
    created_at: datetime = field(default_factory=_now)
    id: str | None = None

    @classmethod
    def write(cls, text: str, staff_id: str) -> "Answer":
        return cls(text=_clean_text(text, "answer"), staff_id=staff_id)


@dataclass
class Question:
    order_no: str
    customer_id: str
    text: str
    created_at: datetime = field(default_factory=_now)
    answer: Answer | None = None
    id: str | None = None

    @classmethod
    def ask(cls, order_no: str, customer_id: str, text: str) -> "Question":
        return cls(order_no=order_no, customer_id=customer_id, text=_clean_text(text, "question"))

    @property
    def is_answered(self) -> bool:
        return self.answer is not None
