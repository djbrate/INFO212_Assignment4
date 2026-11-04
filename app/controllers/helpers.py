"""Small helpers shared by the controllers."""
from __future__ import annotations

from functools import wraps

from flask import abort, current_app, flash, redirect, request, session, url_for

from ..models.repositories.base import Repositories
from ..models.services.image_service import ImageService
from ..models.validation import ValidationError


def repos() -> Repositories:
    return current_app.extensions["repos"]


def images() -> ImageService:
    return current_app.extensions["images"]


def flash_errors(error: ValidationError | ValueError) -> None:
    for message in getattr(error, "errors", [str(error)]):
        flash(message, "error")


def current_customer_id() -> str | None:
    return session.get("customer_id")


def login_required(view):
    """Customers must be logged in (FR-C3.1, FR-C4.1)."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_customer_id() or repos().customers.get(current_customer_id()) is None:
            session.pop("customer_id", None)
            flash("Please log in first.", "info")
            return redirect(url_for("account.login", next=request.full_path))
        return view(*args, **kwargs)

    return wrapped


def get_own_order_or_404(order_no: str):
    """FR-C4.2: customers can only see their own orders. Other orders look like they do not exist."""
    order = repos().orders.get(order_no)
    if order is None or order.customer_id != current_customer_id():
        abort(404)
    return order


def safe_next(target: str | None) -> str | None:
    """Only allow redirects to paths on this site."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None
