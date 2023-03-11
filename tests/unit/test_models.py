import json

from order_service.domain.models import Order, Product, User


def test_create_new_order():
    with open("resources/models/product.json") as product_file:
        product_json = product_file.read()
        product = Product.from_json(json.loads(product_json))
    assert product == Product(code="family-box", name="Family Box", price=14.99)

    with open("resources/models/user.json") as user_file:
        user_json = user_file.read()
        user = User.from_json(json.loads(user_json))
    assert user == User(user_id="e6f24d7d1c7e", first_name="Alan", last_name="Turing")

    order = Order(order_id="test", user=user, product=product)
    assert order.user_id == user.user_id
    assert order.product_name == product.name
