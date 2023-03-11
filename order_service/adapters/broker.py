import abc
import datetime
import json
import logging
from collections import deque

import aio_pika
from tenacity import retry, stop_after_attempt, wait_fixed

from conf import conf
from order_service.domain.models import Order

logger = logging.getLogger(__name__)


class AbstractBroker(abc.ABC):
    @abc.abstractmethod
    async def publish(self, order: Order):
        raise NotImplementedError

    @abc.abstractmethod
    async def initialize(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_initialized(self):
        raise NotImplementedError

    def _serialize_order(self, order: Order):
        return json.dumps(
            {
                "producer": "producer",
                "sent_at": datetime.datetime.now(),
                "type": "order",
                "payload": {
                    "order": {
                        "order_id": order.id,
                        "customer_fullname": order.customer_fullname,
                        "product_name": order.product_name,
                        "total_amount": order.total_amount,
                        "created_at": order.created_at,
                    }
                },
            },
            default=str,
        )


class RabbitMQBroker(AbstractBroker):
    aio_pika.logger.setLevel(logging.ERROR)
    routing_key = "created_order"
    # retry requests to broker in case of failure
    RETRY_COUNT = 3
    WAIT_TO_RETRY_SEC = 3

    def __init__(self, host: str, port: int, login: str, password: str):
        self.exchange = None
        self.connection = None
        self._host = host
        self._port = port
        self._login = login
        self._password = password
        self.channel = None

    @retry(
        stop=stop_after_attempt(RETRY_COUNT),
        reraise=True,
    )
    async def initialize(self):
        self.connection = await aio_pika.connect_robust(
            host=self._host,
            port=self._port,
            login=self._login,
            password=self._password,
        )
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            conf.RABBIT_MQ["parameters"].get("exchange"), durable=True
        )
        logger.info(f"RabbitMQ has been initialized. {self._host}:{self._port}")

    @retry(
        wait=wait_fixed(WAIT_TO_RETRY_SEC),
        stop=stop_after_attempt(RETRY_COUNT),
        reraise=True,
    )
    async def publish(self, order: Order):
        if not self.is_initialized:
            await self.initialize()
        await self.exchange.publish(
            aio_pika.Message(body=self._serialize_order(order).encode()),
            routing_key=self.routing_key,
        )

        logger.info(f"Order msg published. order_id={order.id}")

    @property
    def is_initialized(self):
        return self.connection and not self.connection.is_closed and self.channel


class FakeBroker(AbstractBroker):
    def __init__(self):
        self._deque = deque()

    async def initialize(self):
        pass

    @property
    def is_initialized(self):
        return True

    async def publish(self, order: Order):
        self._deque.append(order)

    def pop(self):
        return self._deque.pop()
