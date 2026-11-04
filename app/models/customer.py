"""Customers (Customer nodes, requirements DR-6; login FR-C3.1, NFR-4)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from .validation import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


@dataclass
class Customer:
    name: str
    email: str
    password_hash: str
    created_at: datetime = field(default_factory=lambda: datetime.now().replace(microsecond=0))
    id: str | None = None

    @classmethod
    def register(cls, name: str, email: str, password: str) -> "Customer":
        """Create a customer with a hashed password (NFR-4). Never stores the plain password."""
        name = (name or "").strip()
        email = (email or "").strip().lower()
        errors = []
        if not name:
            errors.append("Name is required.")
        if not EMAIL_RE.match(email):
            errors.append("Please enter a valid e-mail address.")
        if len(password or "") < MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        if errors:
            raise ValidationError(errors)
        return cls(name=name, email=email, password_hash=generate_password_hash(password))

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password or "")
