"""CONTROLLER – admin panel for Ekte Mat staff.

CLAUDE.md (Admin panel 1–4); requirements FR-A0.1–0.2, FR-A1.1–1.5, FR-A2.1–2.4,
FR-A3.1–3.5, FR-A4.1–4.2.

No login for now (FR-A0.1, team decision 2026-11-04). Every admin route is in
this blueprint, so a staff check can later be added once with `bp.before_request`.
"""
from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..models.enums import Allergen, DietaryLabel, OrderStatus, PaymentStatus
from ..models.food_item import FoodItem
from ..models.question import Answer
from ..models.validation import ValidationError, check_min_order, check_price, parse_int, parse_iso_date
from .helpers import flash_errors, images, repos, safe_next

bp = Blueprint("admin", __name__)


@bp.route("/")
def dashboard():
    orders = repos().orders.list_all()
    return render_template(
        "admin/dashboard.html",
        item_count=len(repos().food_items.list_all()),
        new_orders=[o for o in orders if o.status == OrderStatus.SUBMITTED],
        unanswered=repos().questions.list_all(unanswered_only=True),
    )


# ---- 1. food items ---------------------------------------------------------
def _get_item_or_404(item_id) -> FoodItem:
    item = repos().food_items.get(item_id)
    if item is None:
        abort(404)
    return item


def _item_from_form(form, item: FoodItem | None = None) -> FoodItem:
    """Build a FoodItem from the form and check FR-A1.5 (price > 0, minimum order >= 1)."""
    errors = []
    name = form.get("name", "").strip()
    if not name:
        errors.append("Name is required.")
    price = min_order = None
    try:
        price = parse_int(form.get("price_nok"), "Price")
        errors += check_price(price)
    except ValidationError as err:
        errors += err.errors
    try:
        min_order = parse_int(form.get("min_order"), "Minimum order")
        errors += check_min_order(min_order)
    except ValidationError as err:
        errors += err.errors
    if errors:
        raise ValidationError(errors)
    known = {c.slug for c in repos().categories.list_all()}
    return FoodItem(
        id=item.id if item else None,
        image_path=item.image_path if item else None,
        name=name,
        description=form.get("description", "").strip(),
        price_nok=price,
        min_order=min_order,
        categories=[c for c in form.getlist("categories") if c in known],
        allergens=Allergen.parse_many(form.getlist("allergens")),
        dietary_labels=DietaryLabel.parse_many(form.getlist("dietary_labels")),
        published=form.get("published") == "on",
    )


def _item_form(item, status=200):
    return render_template(
        "admin/item_form.html",
        item=item,
        categories=repos().categories.list_all(),
        allergens=list(Allergen),
        dietary_labels=list(DietaryLabel),
    ), status


@bp.route("/items")
def items():
    return render_template("admin/items.html", items=repos().food_items.list_all(),
                           categories={c.slug: c.name for c in repos().categories.list_all()})


@bp.route("/items/new", methods=["GET", "POST"])
def item_new():
    if request.method == "POST":
        try:
            item = repos().food_items.save(_item_from_form(request.form))
        except ValidationError as err:
            flash_errors(err)
            return _item_form(_form_echo(request.form), 400)
        flash(f"{item.name} was added. You can now add a picture.", "success")
        return redirect(url_for("admin.item_image", item_id=item.id))
    return _item_form(None)


@bp.route("/items/<item_id>/edit", methods=["GET", "POST"])
def item_edit(item_id):
    item = _get_item_or_404(item_id)
    if request.method == "POST":
        try:
            item = repos().food_items.save(_item_from_form(request.form, item))
        except ValidationError as err:
            flash_errors(err)
            echo = _form_echo(request.form)
            echo.id, echo.image_path = item.id, item.image_path
            return _item_form(echo, 400)
        flash(f"{item.name} was saved.", "success")
        return redirect(url_for("admin.items"))
    return _item_form(item)


@bp.post("/items/<item_id>/delete")
def item_delete(item_id):
    item = _get_item_or_404(item_id)
    repos().food_items.delete(item.id)
    images().delete(item.image_path)
    flash(f"{item.name} was removed.", "success")
    return redirect(url_for("admin.items"))


def _form_echo(form) -> FoodItem:
    """Re-show what the user typed after a validation error."""
    def as_int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return v
    return FoodItem(
        name=form.get("name", ""), description=form.get("description", ""),
        price_nok=as_int(form.get("price_nok")), min_order=as_int(form.get("min_order")),
        categories=form.getlist("categories"),
        allergens=Allergen.parse_many(form.getlist("allergens")),
        dietary_labels=DietaryLabel.parse_many(form.getlist("dietary_labels")),
        published=form.get("published") == "on",
    )


# ---- 2. images (upload or AI instruction → preview → confirm) --------------
@bp.route("/items/<item_id>/image")
def item_image(item_id):
    return render_template("admin/item_image.html", item=_get_item_or_404(item_id))


@bp.post("/items/<item_id>/image/upload")
def item_image_upload(item_id):
    item = _get_item_or_404(item_id)
    file = request.files.get("picture")
    try:
        if file is None or not file.filename:
            raise ValueError("Please choose a picture to upload.")
        token = images().pending_from_upload(file.filename, file.read())
    except ValueError as err:
        flash(str(err), "error")
        return redirect(url_for("admin.item_image", item_id=item.id))
    return redirect(url_for("admin.item_image_preview", item_id=item.id, token=token))


@bp.post("/items/<item_id>/image/generate")
def item_image_generate(item_id):
    """FR-A2.2: an instruction to an image service creates a new picture or modifies the current one."""
    item = _get_item_or_404(item_id)
    modify = request.form.get("mode") == "modify"
    try:
        token = images().pending_from_instruction(
            request.form.get("instruction", ""), item.image_path if modify else None
        )
    except Exception as err:  # provider errors are shown to staff, never crash the page
        flash(str(err), "error")
        return redirect(url_for("admin.item_image", item_id=item.id))
    return redirect(url_for("admin.item_image_preview", item_id=item.id, token=token))


@bp.route("/items/<item_id>/image/preview/<token>")
def item_image_preview(item_id, token):
    """FR-A2.3: staff see the picture before it is saved."""
    item = _get_item_or_404(item_id)
    if not images().pending_exists(token):
        flash("The preview has expired. Please create the picture again.", "error")
        return redirect(url_for("admin.item_image", item_id=item.id))
    return render_template("admin/image_preview.html", item=item, token=token,
                           preview_path=images().pending_relpath(token))


@bp.post("/items/<item_id>/image/confirm")
def item_image_confirm(item_id):
    item = _get_item_or_404(item_id)
    try:
        new_path = images().confirm(request.form.get("token", ""), item.id)
    except ValueError as err:
        flash(str(err), "error")
        return redirect(url_for("admin.item_image", item_id=item.id))
    old_path = item.image_path
    item.image_path = new_path
    repos().food_items.save(item)
    images().delete(old_path)
    flash("The picture was saved.", "success")
    return redirect(url_for("admin.items"))


@bp.post("/items/<item_id>/image/discard")
def item_image_discard(item_id):
    item = _get_item_or_404(item_id)
    images().discard(request.form.get("token", ""))
    flash("The picture was discarded.", "info")
    return redirect(url_for("admin.item_image", item_id=item.id))


# ---- 3. orders -------------------------------------------------------------
def _get_order_or_404(order_no):
    order = repos().orders.get(order_no)
    if order is None:
        abort(404)
    return order


@bp.route("/orders")
def orders():
    """FR-A3.1: all orders, filtered by status and event date."""
    status_raw = request.args.get("status", "")
    status = OrderStatus(status_raw) if status_raw in {s.value for s in OrderStatus} else None
    date_from = parse_iso_date(request.args.get("date_from"))
    date_to = parse_iso_date(request.args.get("date_to"))
    orders = repos().orders.list_all(status=status, date_from=date_from, date_to=date_to)
    customers = {o.customer_id: repos().customers.get(o.customer_id) for o in orders}
    return render_template("admin/orders.html", orders=orders, customers=customers,
                           filters={"status": status_raw, "date_from": request.args.get("date_from", ""),
                                    "date_to": request.args.get("date_to", "")})


@bp.route("/orders/<order_no>")
def order_detail(order_no):
    order = _get_order_or_404(order_no)
    return render_template(
        "admin/order_detail.html",
        order=order,
        customer=repos().customers.get(order.customer_id),
        questions=repos().questions.list_for_order(order.order_no),
    )


@bp.post("/orders/<order_no>/status")
def order_status(order_no):
    """FR-A3.3: only the transitions in the state machine are allowed."""
    order = _get_order_or_404(order_no)
    try:
        order.change_status(OrderStatus(request.form.get("status", "")))
    except ValueError as err:  # unknown value or InvalidTransition
        flash_errors(err if isinstance(err, ValidationError) else ValidationError("Unknown order status."))
        return redirect(url_for("admin.order_detail", order_no=order.order_no))
    repos().orders.save(order)
    flash(f"Order {order.order_no} is now {order.status.label.lower()}.", "success")
    return redirect(url_for("admin.order_detail", order_no=order.order_no))


@bp.post("/orders/<order_no>/payment")
def order_payment(order_no):
    """FR-A3.4: payment status set by hand."""
    order = _get_order_or_404(order_no)
    try:
        order.set_payment_status(PaymentStatus(request.form.get("payment_status", "")))
    except ValueError:
        flash("Unknown payment status.", "error")
        return redirect(url_for("admin.order_detail", order_no=order.order_no))
    repos().orders.save(order)
    flash(f"Payment status for {order.order_no}: {order.payment_status.label.lower()}.", "success")
    return redirect(url_for("admin.order_detail", order_no=order.order_no))


# ---- 4. questions ----------------------------------------------------------
@bp.route("/questions")
def questions():
    unanswered_only = request.args.get("unanswered") == "1"
    return render_template("admin/questions.html", questions=repos().questions.list_all(unanswered_only),
                           unanswered_only=unanswered_only)


@bp.post("/questions/<question_id>/answer")
def answer_question(question_id):
    """FR-A4.2: staff write an answer that the customer sees on the order."""
    question = repos().questions.get(question_id)
    if question is None:
        abort(404)
    try:
        answer = Answer.write(request.form.get("text", ""), repos().staff.get_default().id)
    except ValidationError as err:
        flash_errors(err)
    else:
        repos().questions.add_answer(question.id, answer)
        flash("The answer was sent to the customer.", "success")
    return redirect(safe_next(request.form.get("back")) or url_for("admin.order_detail", order_no=question.order_no))
