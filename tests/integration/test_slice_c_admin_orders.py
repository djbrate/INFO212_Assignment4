"""Slice C – admin orders and questions.

FR-A3.1–3.5, FR-A4.1–4.2, FR-C5.1–5.2.
"""
from datetime import date, timedelta

import pytest

from app.models.enums import OrderStatus, PaymentStatus
from app.models.order import GuestGroupNote, Order, OrderItem
from tests.conftest import login


@pytest.fixture
def orders(repos, customer, soup):
    def make(days, guests):
        return repos.orders.save(Order(
            customer_id=customer.id, event_date=date.today() + timedelta(days=days), guests=guests,
            delivery_address="Bryggen 1", items=[OrderItem(soup.id, soup.name, guests, soup.price_nok)],
            notes=[GuestGroupNote("nut allergy", 2)]))
    return [make(5, 10), make(20, 30)]


def test_order_list_and_filters(client, repos, orders):
    first, second = orders
    approved = repos.orders.get(second.order_no)
    approved.change_status(OrderStatus.APPROVED)
    repos.orders.save(approved)

    html = client.get("/admin/orders").get_data(as_text=True)
    assert first.order_no in html and second.order_no in html

    html = client.get("/admin/orders?status=approved").get_data(as_text=True)
    assert second.order_no in html and first.order_no not in html

    cut = (date.today() + timedelta(days=10)).isoformat()
    html = client.get(f"/admin/orders?date_from={cut}").get_data(as_text=True)
    assert second.order_no in html and first.order_no not in html
    html = client.get(f"/admin/orders?date_to={cut}").get_data(as_text=True)
    assert first.order_no in html and second.order_no not in html


def test_order_page_highlights_allergies(client, orders):
    html = client.get(f"/admin/orders/{orders[0].order_no}").get_data(as_text=True)
    assert 'class="allergy-box"' in html and "nut allergy" in html
    assert "Kari" in html and "1 890 NOK" in html


def test_status_change_follows_state_machine(client, repos, orders):
    no = orders[0].order_no
    client.post(f"/admin/orders/{no}/status", data={"status": "approved"})
    assert repos.orders.get(no).status == OrderStatus.APPROVED

    r = client.post(f"/admin/orders/{no}/status", data={"status": "delivered"}, follow_redirects=True)
    assert "cannot go from approved to delivered" in r.get_data(as_text=True)
    assert repos.orders.get(no).status == OrderStatus.APPROVED

    client.post(f"/admin/orders/{no}/status", data={"status": "nonsense"})
    assert repos.orders.get(no).status == OrderStatus.APPROVED


def test_payment_status_set_by_hand(client, repos, orders):
    no = orders[0].order_no
    client.post(f"/admin/orders/{no}/payment", data={"payment_status": "deposit_paid"})
    assert repos.orders.get(no).payment_status == PaymentStatus.DEPOSIT_PAID


def test_question_answer_round_trip(client, repos, orders):
    no = orders[0].order_no
    login(client)
    client.post(f"/orders/{no}/questions", data={"text": "Can you deliver at 11:30?"})
    [q] = repos.questions.list_for_order(no)
    assert "Unanswered" in client.get("/admin/questions?unanswered=1").get_data(as_text=True)

    client.post(f"/admin/questions/{q.id}/answer", data={"text": "Yes, 11:30 is fine."})
    assert repos.questions.get(q.id).is_answered
    assert repos.questions.list_all(unanswered_only=True) == []

    page = client.get(f"/orders/{no}").get_data(as_text=True)  # customer sees the answer (FR-C5.2)
    assert "Yes, 11:30 is fine." in page


def test_empty_question_or_answer_is_refused(client, repos, orders):
    no = orders[0].order_no
    login(client)
    client.post(f"/orders/{no}/questions", data={"text": "   "})
    assert repos.questions.list_for_order(no) == []
