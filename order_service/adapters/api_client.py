import abc
import logging
from typing import Type, Union

import aiohttp

from order_service.domain.models import Product, User

logger = logging.getLogger(__name__)


class AbstractAPIClient(abc.ABC):
    @abc.abstractmethod
    async def get_user(self, user_id: str) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_product(self, user_id: str) -> Product:
        raise NotImplementedError


class APIClient(AbstractAPIClient):
    """Client to access to User and Product information."""
    TIMEOUT = timeout = aiohttp.ClientTimeout(total=5)

    def __init__(self, services_endpoints: dict):
        self._services_endpoints = services_endpoints

    async def get_user(self, user_id: str) -> User:
        user = await self._get_object_by_id(user_id, User)
        logger.debug(f"Got user {user}")
        return user

    async def get_product(self, product_id: str) -> Product:
        product = await self._get_object_by_id(product_id, Product)
        logger.debug(f"Got product {product}")
        return product

    async def _get_object_by_id(
        self, object_id: str, object_type: Union[Type[User], Type[Product]]
    ):
        object_endpoint = self._services_endpoints.get(object_type.resource_name)
        async with aiohttp.ClientSession(raise_for_status=True, timeout=APIClient.TIMEOUT) as session:
            object_url = f'{object_endpoint.get("url")}{object_id}'
            logger.debug(f"GET {object_url}")
            async with session.get(object_url) as resp:
                object_json = await resp.json()
            return object_type.from_json(object_json)


class FakeAPIClient(AbstractAPIClient):
    def __init__(
        self,
        user: User = User("123", "Jonh", "Smith"),
        product: Product = Product("123", "meat", 9.99),
        faulty: bool = False,
    ):
        self.user = user
        self.product = product
        self.faulty = faulty

    async def get_user(self, user_id: str):
        if self.faulty:
            raise aiohttp.ClientResponseError(None, None)
        return self.user

    async def get_product(self, user_id: str) -> Product:
        return self.product
