"""CONTROLLER – customer shop: menu by event and shopping cart.

CLAUDE.md (Customer Site 1–2); requirements FR-C1.1–1.2, FR-C2.1–2.4.
"""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..models.cart import Cart
from ..models.validation import ValidationError
from .helpers import flash_errors, repos, safe_next

bp = Blueprint("shop", __name__)


@bp.route("/")
def home():
    categories = repos().categories.list_all()
    return render_template("shop/home.html", categories=categories)


@bp.route("/menu")
def menu():
    """Published items as cards, grouped by event category (FR-C1.1). An item can be in several groups."""
    categories = repos().categories.list_all()
    items = repos().food_items.list_published()
    selected = request.args.get("event")
    groups = []
    for category in categories:
        if selected and category.slug != selected:
            continue
        in_group = [item for item in items if category.slug in item.categories]
        if in_group:
            groups.append((category, in_group))
    if not selected:
        uncategorised = [item for item in items if not item.categories]
        if uncategorised:
            groups.append((None, uncategorised))
    return render_template("shop/menu.html", groups=groups, categories=categories, selected=selected)


@bp.route("/cart")
def cart():
    cart = Cart.from_session(session)
    lines = cart.lines(repos().food_items)
    return render_template("shop/cart.html", lines=lines, total=sum(l.line_total for l in lines))


@bp.post("/cart/add")
def cart_add():
    """Add an item, or change its quantity if it is already in the cart (FR-C2.1, FR-C2.3)."""
    item = repos().food_items.get(request.form.get("item_id", ""))
    if item is None:
        flash("That item no longer exists.", "error")
        return redirect(url_for("shop.menu"))
    cart = Cart.from_session(session)
    try:
        cart.set(item, request.form.get("quantity"))
    except ValidationError as err:
        flash_errors(err)
        return redirect(safe_next(request.form.get("back")) or url_for("shop.menu"))
    cart.save(session)
    flash(f"{item.name} × {cart.quantity_of(item.id)} is in your cart.", "success")
    return redirect(safe_next(request.form.get("back")) or url_for("shop.menu"))


@bp.post("/cart/update")
def cart_update():
    """Change the quantities of all lines at once from the cart page."""
    cart = Cart.from_session(session)
    errors = False
    for line in cart.lines(repos().food_items):
        raw = request.form.get(f"qty_{line.item.id}")
        if raw is None:
            continue
        try:
            cart.set(line.item, raw)
        except ValidationError as err:
            flash_errors(err)
            errors = True
    cart.save(session)
    if not errors:
        flash("Cart updated.", "success")
    return redirect(url_for("shop.cart"))


@bp.post("/cart/remove/<item_id>")
def cart_remove(item_id):
    cart = Cart.from_session(session)
    cart.remove(item_id)
    cart.save(session)
    flash("Item removed from the cart.", "success")
    return redirect(url_for("shop.cart"))
