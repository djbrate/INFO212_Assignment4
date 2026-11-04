"""Ekte Mat staff (Staff nodes, requirements DR-6)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Staff:
    """Ekte Mat staff member. Writes answers to questions. No login yet (FR-A0.1)."""

    name: str
    email: str
    id: str | None = None
