"""Event categories (EventCategory nodes, requirements DR-6)."""
from dataclasses import dataclass


@dataclass
class EventCategory:
    slug: str
    name: str
    sort_order: int = 0


# The categories named in CLAUDE.md (Context; Customer Site 1) and
# docs/requirements.md section 5. Used by seed.py.
DEFAULT_CATEGORIES = [
    EventCategory("corporate-lunch", "Corporate lunch", 1),
    EventCategory("conference", "Conference", 2),
    EventCategory("private-party", "Private party", 3),
    EventCategory("birthday", "Birthday", 4),
    EventCategory("confirmation", "Confirmation", 5),
    EventCategory("wedding", "Wedding", 6),
    EventCategory("christmas-party", "Christmas party (julebord)", 7),
    EventCategory("other", "Other events", 8),
]
