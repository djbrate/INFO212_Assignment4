"""Every page renders, shop and admin share one layout (NFR-2a), and the seed data works."""
from seed import seed


def test_all_main_pages_render_with_seed_data(client, app, repos):
    data = seed(repos, app.extensions["images"])
    order = data["orders"][0]
    item = next(iter(data["items"].values()))
    for url in ["/", "/menu", "/cart", "/login", "/register", "/admin/", "/admin/items", "/admin/items/new",
                f"/admin/items/{item.id}/edit", f"/admin/items/{item.id}/image", "/admin/orders",
                f"/admin/orders/{order.order_no}", "/admin/questions"]:
        r = client.get(url)
        assert r.status_code == 200, url
        assert 'class="topbar"' in r.get_data(as_text=True), url  # shared layout


def test_admin_pages_use_admin_navigation(client):
    html = client.get("/admin/").get_data(as_text=True)
    assert "Admin panel" in html and "area-admin" in html


def test_seed_is_idempotent(app, repos):
    seed(repos, app.extensions["images"])
    seed(repos, app.extensions["images"])
    assert len(repos.food_items.list_all()) == 10
    assert len(repos.orders.list_all()) == 3


def test_dates_and_money_format(app):
    from datetime import date
    nok = app.jinja_env.filters["nok"]
    isodate = app.jinja_env.filters["isodate"]
    assert nok(12450) == "12 450 NOK"
    assert isodate(date(2026, 12, 1)) == "2026-12-01"
