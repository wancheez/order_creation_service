import asyncio
import logging
import uuid
from typing import Optional

from order_service.adapters.api_client import AbstractAPIClient
from order_service.adapters.broker import AbstractBroker
from order_service.adapters.repository import AbstractRepository
from order_service.dependency.injector import DependencyInjector
from order_service.domain.models import Order

logger = logging.getLogger(__name__)
injector = DependencyInjector()


async def send_order(
    user_id: str,
    product_code: str,
    repository: AbstractRepository = injector.provide(AbstractRepository),
    api_client: AbstractAPIClient = injector.provide(AbstractAPIClient),
    broker: AbstractBroker = injector.provide(AbstractBroker),
) -> str:
    """Send order to DB and RabbitMQ.

    Args:
        user_id: user_id
        product_code: product_code
        repository: repository to save order
        api_client: to retrieve user and product info
        broker: to send order
    Returns:
        new order id
    """
    user = await api_client.get_user(user_id)
    product = await api_client.get_product(product_code)
    order_id = str(uuid.uuid4())
    order = Order(order_id, user, product)
    repository.add(order)
    # will not make a client to wait until the broker is recovered in case of failures
    # status of the order might be controlled with a Status parameter in database (not implemented now)
    # hence run publishing in non-blocking coroutine, where attempts might be repeated
    asyncio.create_task(_run_publish_async(order, broker))
    return order_id


async def get_order(
        order_id: str,
        repository: AbstractRepository = injector.provide(AbstractRepository),
) -> Optional[Order]:
    order_obj = repository.get(order_id)
    return order_obj


async def get_orders(
        repository: AbstractRepository = injector.provide(AbstractRepository),
) -> Optional[list[Order]]:
    order_obj = repository.list()
    return order_obj


async def _run_publish_async(order: Order, broker: AbstractBroker):
    await broker.publish(order)
