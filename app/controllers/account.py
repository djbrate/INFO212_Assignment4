"""CONTROLLER – customer account: register, log in, submit order, my orders, questions.

CLAUDE.md (Customer Site 3–5); requirements FR-C3.1–3.5, FR-C4.1–4.2, FR-C5.1–5.2, NFR-4.
"""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..models.cart import Cart
from ..models.customer import Customer
from ..models.order import GuestGroupNote, Order
from ..models.question import Question
from ..models.validation import MAX_GUESTS, ValidationError, parse_int, parse_iso_date
from .helpers import current_customer_id, flash_errors, get_own_order_or_404, login_required, repos, safe_next

bp = Blueprint("account", __name__)


# ---- register / log in -----------------------------------------------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            customer = Customer.register(
                request.form.get("name", ""), request.form.get("email", ""), request.form.get("password", "")
            )
            if request.form.get("password") != request.form.get("password2"):
                raise ValidationError("The two passwords do not match.")
            customer = repos().customers.save(customer)
        except ValidationError as err:
            flash_errors(err)
            return render_template("account/register.html", form=request.form), 400
        session.clear()
        session["customer_id"] = customer.id
        flash(f"Welcome, {customer.name}!", "success")
        return redirect(safe_next(request.args.get("next")) or url_for("shop.menu"))
    return render_template("account/register.html", form={})


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        customer = repos().customers.get_by_email(request.form.get("email", ""))
        if customer is None or not customer.check_password(request.form.get("password", "")):
            flash("Wrong e-mail or password.", "error")
            return render_template("account/login.html", form=request.form), 401
        cart = session.get("cart")  # keep the cart the visitor filled before logging in
        session.clear()
        if cart:
            session["cart"] = cart
        session["customer_id"] = customer.id
        flash(f"Logged in as {customer.name}.", "success")
        return redirect(safe_next(request.args.get("next")) or url_for("account.orders"))
    return render_template("account/login.html", form={})


@bp.post("/logout")
def logout():
    session.clear()
    flash("You are logged out.", "info")
    return redirect(url_for("shop.home"))


# ---- submit order ----------------------------------------------------------
def _notes_from_form(form) -> list[GuestGroupNote]:
    """Allergy and dietary notes per guest group, e.g. "nut allergy" × 2 (FR-C3.2, FR-C3.3)."""
    notes = []
    for label, count in zip(form.getlist("note_label"), form.getlist("note_count")):
        label = label.strip()
        if not label and not count.strip():
            continue  # empty row
        notes.append(GuestGroupNote(label=label, count=parse_int(count or "0", "Number of guests in a note")))
    return notes


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = Cart.from_session(session)
    lines = cart.lines(repos().food_items)
    if not lines:
        flash("Your cart is empty.", "info")
        return redirect(url_for("shop.menu"))
    total = sum(l.line_total for l in lines)

    if request.method == "POST":
        try:
            errors = []
            event_date = parse_iso_date(request.form.get("event_date"))
            try:
                guests = parse_int(request.form.get("guests"), "Number of guests")
            except ValidationError as err:
                errors += err.errors
                guests = 0
            try:
                notes = _notes_from_form(request.form)
            except ValidationError as err:
                errors += err.errors
                notes = []
            order = Order(
                customer_id=current_customer_id(),
                event_date=event_date,
                guests=guests,
                delivery_address=request.form.get("delivery_address", "").strip(),
                items=cart.to_order_items(repos().food_items),
                notes=notes,
            )
            try:
                order.validate()
            except ValidationError as err:
                errors += err.errors
            if errors:
                raise ValidationError(errors)
        except ValidationError as err:
            flash_errors(err)
            return render_template("account/checkout.html", lines=lines, total=total, form=request.form,
                                   max_guests=MAX_GUESTS), 400
        order = repos().orders.save(order)  # status "submitted", payment "not paid" (FR-C3.5)
        cart.clear()
        cart.save(session)
        flash(f"Thank you! Your order {order.order_no} has been sent to Ekte Mat.", "success")
        return redirect(url_for("account.order_detail", order_no=order.order_no))

    return render_template("account/checkout.html", lines=lines, total=total, form={}, max_guests=MAX_GUESTS)


# ---- my orders and questions -----------------------------------------------
@bp.route("/orders")
@login_required
def orders():
    return render_template("account/orders.html", orders=repos().orders.list_for_customer(current_customer_id()))


@bp.route("/orders/<order_no>")
@login_required
def order_detail(order_no):
    order = get_own_order_or_404(order_no)
    questions = repos().questions.list_for_order(order.order_no)
    return render_template("account/order_detail.html", order=order, questions=questions)


@bp.post("/orders/<order_no>/questions")
@login_required
def ask_question(order_no):
    """FR-C5.1: ask a question about one of your own orders."""
    order = get_own_order_or_404(order_no)
    try:
        question = Question.ask(order.order_no, current_customer_id(), request.form.get("text", ""))
    except ValidationError as err:
        flash_errors(err)
    else:
        repos().questions.save(question)
        flash("Your question has been sent. You will see the answer here.", "success")
    return redirect(url_for("account.order_detail", order_no=order.order_no) + "#questions")
