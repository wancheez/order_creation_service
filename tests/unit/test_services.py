import asyncio

import aiohttp
import pytest

from order_service.adapters.api_client import FakeAPIClient
from order_service.adapters.broker import FakeBroker
from order_service.adapters.repository import FakeRepository
from order_service.domain.models import Order, Product, User
from order_service.service_layer.services import send_order


@pytest.mark.asyncio
async def test_create_order():
    product = Product(code="classic-box", name="Classic Box", price=9.99)
    user = User(user_id="7c11e1ce2741", first_name="Ada", last_name="Lovelace")

    repo = FakeRepository(set())
    broker = FakeBroker()
    api_client = FakeAPIClient(user=user, product=product)
    order_id = await send_order(
        user_id="7c11e1ce2741",
        product_code="classic-box",
        repository=repo,
        broker=broker,
        api_client=api_client,
    )
    order_from_repo: Order = repo.get(order_id)
    assert order_from_repo == Order(
        order_id, user, product
    ), "The order wasn't added to the repository"
    await asyncio.sleep(0.1)  # wait async publishing of broker
    assert broker.pop() == Order(order_id, user, product)


@pytest.mark.asyncio
async def test_failed_create_order():
    repo = FakeRepository(set())
    broker = FakeBroker()
    api_client = FakeAPIClient(faulty=True)
    with pytest.raises(aiohttp.ClientResponseError):
        await send_order(
            user_id="e6f24d7d1c7e",
            product_code="classic-box",
            repository=repo,
            broker=broker,
            api_client=api_client,
        )
