import asyncio
import logging
from typing import Optional

from sqlalchemy import URL, create_engine

from conf import conf
from order_service.adapters import orm
from order_service.adapters.api_client import AbstractAPIClient, APIClient
from order_service.adapters.broker import AbstractBroker, RabbitMQBroker
from order_service.adapters.repository import (AbstractRepository,
                                               SqlAlchemyRepository)


class DependencyInjector:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(DependencyInjector, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._broker: Optional[AbstractBroker] = None
        self._repository: Optional[AbstractRepository] = None
        self._api_client = None
        self._deps = {
            AbstractRepository: self.repository,
            AbstractBroker: self.broker,
            AbstractAPIClient: self.api_client,
        }

    def repository(self) -> AbstractRepository:
        if self._repository:
            return self._repository
        orm.start_mappers()
        db_conf = conf.DATABASE
        db_type = db_conf.get("type", "sqlite")
        if db_type == "sqlite":
            repo = SqlAlchemyRepository(create_engine("sqlite:///:memory:"))
        elif db_type == "postgres":
            url = URL.create(
                drivername="postgresql",
                username=db_conf.get("username"),
                host=db_conf.get("host"),
                password=db_conf.get("password"),
                database=db_conf.get("database"),
            )
            repo = SqlAlchemyRepository(create_engine(url))
        else:
            raise ValueError(f"The {db_type} is unrecognized")

        self._repository = repo
        return self._repository

    def broker(self) -> AbstractBroker:
        if self._broker:
            return self._broker
        rabbit_conf = conf.RABBIT_MQ["parameters"]
        broker = RabbitMQBroker(
            rabbit_conf.get("host"),
            rabbit_conf.get("port"),
            rabbit_conf.get("login"),
            rabbit_conf.get("password"),
        )
        self._broker = broker
        return broker

    def api_client(self) -> AbstractAPIClient:
        if self._api_client:
            return self._api_client
        api_client = APIClient(conf.SERVICES_ENDPOINTS)
        self._api_client = api_client
        return api_client

    def provide(self, dep_type):
        if dep := self._deps.get(dep_type):
            return dep()
        raise ValueError(f"Dependency for {dep_type} is not configured")
