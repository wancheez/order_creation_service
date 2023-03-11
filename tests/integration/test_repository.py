from sqlalchemy import text

from order_service.adapters.repository import SqlAlchemyRepository
from order_service.domain.models import Order, Product, User


def insert_order(repo):
    repo.execute(
        text(
            "INSERT INTO orders (id, user_id, product_code, customer_fullname, product_name, total_amount, created_at)"
            " VALUES ('order_id1', '1', 'product_code_1', 'John Smith', 'meat', 9.99, '2023-02-11')"
        )
    )
    [[order_id]] = repo.execute(
        text("SELECT id FROM orders WHERE id=:orderid"), dict(orderid="order_id1")
    )
    return order_id


def test_repository_can_get_an_order(engine):
    repo = SqlAlchemyRepository(engine)
    order_id = insert_order(repo)
    order_from_repo = repo.get(order_id)
    user = User(user_id="1", first_name="John", last_name="Smith")
    product = Product(code="product_code_1", name="meat", price=9.99)
    order = Order(order_id="order_id1", user=user, product=product)
    assert order_from_repo == order


def test_repository_can_save_an_order(engine):
    user = User(user_id="1", first_name="John", last_name="Smith")
    product = Product(code="product_code_1", name="meat", price=9.99)
    order = Order(order_id="order_id1", user=user, product=product)

    repo = SqlAlchemyRepository(engine)
    repo.add(order)
    repo.session.commit()
    rows = list(repo.session.query(Order))
    assert rows == [order]
