"""Slice A – admin food items, images and the customer menu.

FR-A1.1–1.5, FR-A2.1–2.3, FR-C1.1–1.2.
"""
import io

from PIL import Image


def item_form(**kw):
    data = {"name": "Voss lamb", "description": "Slow-cooked", "price_nok": "245", "min_order": "10",
            "categories": ["wedding", "birthday"], "allergens": ["celery"], "dietary_labels": ["lactose_free"],
            "published": "on"}
    data.update(kw)
    return data


def test_admin_can_create_edit_and_remove_item(client, repos):
    r = client.post("/admin/items/new", data=item_form())
    assert r.status_code == 302
    [item] = repos.food_items.list_all()
    assert (item.price_nok, item.min_order, item.categories) == (245, 10, ["wedding", "birthday"])
    assert [a.value for a in item.allergens] == ["celery"]

    client.post(f"/admin/items/{item.id}/edit", data=item_form(price_nok="260"))
    assert repos.food_items.get(item.id).price_nok == 260

    client.post(f"/admin/items/{item.id}/delete")
    assert repos.food_items.list_all() == []


def test_invalid_price_or_minimum_is_rejected(client, repos):
    for bad in ({"price_nok": "0"}, {"price_nok": "abc"}, {"min_order": "0"}, {"name": ""}):
        r = client.post("/admin/items/new", data=item_form(**bad))
        assert r.status_code == 400
    assert repos.food_items.list_all() == []
    assert "Price must be greater than 0 NOK." in client.post(
        "/admin/items/new", data=item_form(price_nok="0")).get_data(as_text=True)


def test_menu_shows_only_published_items_grouped_by_event(client, soup, hidden_item):
    html = client.get("/menu").get_data(as_text=True)
    assert "Fish soup" in html and "189" in html and "minimum 10" in html and "Fish" in html
    assert "Secret test dish" not in html
    assert "Corporate lunch" in html  # group heading


def test_menu_filter_by_event(client, soup):
    assert "Fish soup" in client.get("/menu?event=corporate-lunch").get_data(as_text=True)
    assert "Fish soup" not in client.get("/menu?event=wedding").get_data(as_text=True)


def test_generated_image_is_saved_only_after_confirm(client, repos, soup):
    r = client.post(f"/admin/items/{soup.id}/image/generate", data={"instruction": "Fish soup in a bowl"})
    assert r.status_code == 302 and "/preview/" in r.location
    token = r.location.rsplit("/", 1)[1]
    assert repos.food_items.get(soup.id).image_path is None  # not saved yet (FR-A2.3)
    assert client.get(r.location).status_code == 200

    client.post(f"/admin/items/{soup.id}/image/confirm", data={"token": token})
    path = repos.food_items.get(soup.id).image_path
    assert path and path.startswith("items/")
    assert client.get(f"/media/{path}").status_code == 200


def test_uploaded_image_can_be_discarded(client, repos, soup):
    png = io.BytesIO()
    Image.new("RGB", (20, 20), (0, 120, 0)).save(png, format="PNG")
    png.seek(0)
    r = client.post(f"/admin/items/{soup.id}/image/upload", data={"picture": (png, "soup.png")},
                    content_type="multipart/form-data")
    token = r.location.rsplit("/", 1)[1]
    client.post(f"/admin/items/{soup.id}/image/discard", data={"token": token})
    assert repos.food_items.get(soup.id).image_path is None
    assert client.get(f"/admin/items/{soup.id}/image/preview/{token}").status_code == 302  # gone
