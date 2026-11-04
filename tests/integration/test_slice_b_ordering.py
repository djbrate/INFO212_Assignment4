"""Slice B – cart, register/login, submit order, my orders.

FR-C2.1–2.4, FR-C3.1–3.5, FR-C4.1–4.2, NFR-4.
"""
from datetime import date, timedelta

from app.models.enums import OrderStatus, PaymentStatus
from tests.conftest import PASSWORD, login, make_customer


def order_form(event_date, **kw):
    data = {"event_date": event_date, "guests": "12", "delivery_address": "Bryggen 1, 5003 Bergen",
            "note_label": ["nut allergy", "vegan", ""], "note_count": ["2", "3", ""]}
    data.update(kw)
    return data


def test_cart_rejects_quantity_below_minimum(client, soup):
    r = client.post("/cart/add", data={"item_id": soup.id, "quantity": "5"}, follow_redirects=True)
    assert "The minimum order for Fish soup is 10." in r.get_data(as_text=True)
    assert "Your cart is empty" in client.get("/cart").get_data(as_text=True)


def test_cart_add_change_remove_and_total(client, soup):
    client.post("/cart/add", data={"item_id": soup.id, "quantity": "10"})
    assert "1 890 NOK" in client.get("/cart").get_data(as_text=True)
    client.post("/cart/update", data={f"qty_{soup.id}": "12"})
    assert "2 268 NOK" in client.get("/cart").get_data(as_text=True)
    client.post(f"/cart/remove/{soup.id}")
    assert "Your cart is empty" in client.get("/cart").get_data(as_text=True)


def test_register_then_login(client, repos):
    r = client.post("/register", data={"name": "Ola", "email": "ola@example.com",
                                       "password": PASSWORD, "password2": PASSWORD})
    assert r.status_code == 302
    stored = repos.customers.get_by_email("ola@example.com")
    assert stored.password_hash != PASSWORD  # hashed (NFR-4)
    client.post("/logout")
    assert login(client, "ola@example.com").status_code == 302
    assert client.post("/login", data={"email": "ola@example.com", "password": "wrong"}).status_code == 401


def test_duplicate_email_is_refused(client, customer):
    r = client.post("/register", data={"name": "Kari 2", "email": customer.email,
                                       "password": PASSWORD, "password2": PASSWORD})
    assert r.status_code == 400 and "already exists" in r.get_data(as_text=True)


def test_checkout_requires_login(client, soup):
    client.post("/cart/add", data={"item_id": soup.id, "quantity": "10"})
    r = client.get("/checkout")
    assert r.status_code == 302 and "/login" in r.location


def test_submit_order(client, repos, customer, soup, future_date):
    login(client)
    client.post("/cart/add", data={"item_id": soup.id, "quantity": "12"})
    r = client.post("/checkout", data=order_form(future_date))
    assert r.status_code == 302
    [order] = repos.orders.list_for_customer(customer.id)
    assert order.status == OrderStatus.SUBMITTED and order.payment_status == PaymentStatus.NOT_PAID
    assert order.total == 12 * 189
    assert [(n.label, n.count) for n in order.notes] == [("nut allergy", 2), ("vegan", 3)]
    assert client.get("/cart").get_data(as_text=True).count("Your cart is empty") == 1  # cart emptied
    page = client.get(f"/orders/{order.order_no}").get_data(as_text=True)
    assert order.order_no in page and "nut allergy" in page and "Submitted" in page


def test_order_with_past_date_or_bad_guests_is_rejected(client, repos, customer, soup, future_date):
    login(client)
    client.post("/cart/add", data={"item_id": soup.id, "quantity": "12"})
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    for form in (order_form(yesterday), order_form(future_date, guests="0"),
                 order_form(future_date, guests="1001"), order_form(future_date, guests="-3")):
        assert client.post("/checkout", data=form).status_code == 400
    assert repos.orders.list_all() == []


def test_customer_only_sees_own_orders(client, repos, customer, soup, future_date):
    login(client)
    client.post("/cart/add", data={"item_id": soup.id, "quantity": "10"})
    client.post("/checkout", data=order_form(future_date))
    [order] = repos.orders.list_all()
    client.post("/logout")

    make_customer(repos, "other@example.com", "Other")
    login(client, "other@example.com")
    assert order.order_no not in client.get("/orders").get_data(as_text=True)
    assert client.get(f"/orders/{order.order_no}").status_code == 404
    assert client.post(f"/orders/{order.order_no}/questions", data={"text": "Hi?"}).status_code == 404
