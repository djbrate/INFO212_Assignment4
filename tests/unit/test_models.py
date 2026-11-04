"""Food item rules (FR-A1.5), cart (FR-C2.x), customer passwords (NFR-4), questions (FR-C5.1)."""
import pytest

from app.models.cart import Cart
from app.models.customer import Customer
from app.models.food_item import FoodItem
from app.models.question import Answer, Question
from app.models.repositories.fake import FakeFoodItemRepository
from app.models.validation import ValidationError


def item(**kw):
    data = dict(name="Fish soup", description="", price_nok=189, min_order=10, published=True)
    data.update(kw)
    return FoodItem(**data)


def test_valid_food_item():
    item().validate()


@pytest.mark.parametrize("kw", [{"price_nok": 0}, {"price_nok": -5}, {"min_order": 0}, {"name": " "}])
def test_invalid_food_item_is_rejected(kw):
    with pytest.raises(ValidationError):
        item(**kw).validate()


@pytest.fixture
def food_repo():
    repo = FakeFoodItemRepository()
    repo.save(item(id="soup"))
    repo.save(item(id="salad", name="Salad", price_nok=165, min_order=5))
    return repo


def test_cart_total_and_change(food_repo):
    cart = Cart()
    cart.set(food_repo.get("soup"), "12")
    cart.set(food_repo.get("salad"), 5)
    assert cart.total(food_repo) == 12 * 189 + 5 * 165
    cart.set(food_repo.get("soup"), 20)     # change quantity
    cart.remove("salad")
    assert cart.total(food_repo) == 20 * 189
    assert cart.count == 1


@pytest.mark.parametrize("qty", ["9", "0", "-3", "2.5", "ten", ""])
def test_cart_rejects_bad_quantities(food_repo, qty):
    with pytest.raises(ValidationError):
        Cart().set(food_repo.get("soup"), qty)


def test_cart_rejects_unpublished_item():
    with pytest.raises(ValidationError):
        Cart().set(item(id="x", published=False), 10)


def test_cart_to_order_items_keeps_unit_price(food_repo):
    cart = Cart()
    cart.set(food_repo.get("soup"), 10)
    [line] = cart.to_order_items(food_repo)
    assert (line.name, line.quantity, line.unit_price) == ("Fish soup", 10, 189)


def test_password_is_hashed():
    c = Customer.register("Kari", "Kari@Example.com", "long-password")
    assert c.password_hash != "long-password"
    assert c.email == "kari@example.com"
    assert c.check_password("long-password")
    assert not c.check_password("wrong")


@pytest.mark.parametrize("args", [("", "a@b.no", "long-password"), ("Kari", "not-an-email", "long-password"),
                                  ("Kari", "a@b.no", "short")])
def test_register_validation(args):
    with pytest.raises(ValidationError):
        Customer.register(*args)


def test_question_and_answer():
    q = Question.ask("EM-00001", "c1", "  Can you deliver at 11:30?  ")
    assert q.text == "Can you deliver at 11:30?" and not q.is_answered
    q.answer = Answer.write("Yes", "s1")
    assert q.is_answered
    with pytest.raises(ValidationError):
        Question.ask("EM-00001", "c1", "   ")
