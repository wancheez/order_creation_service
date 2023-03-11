import abc
import logging

import sqlalchemy
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from order_service.domain.models import Order

logger = logging.getLogger(__name__)


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, order: Order):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> Order:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, engine: Engine):
        self.session = sessionmaker(bind=engine)()

    def add(self, order):
        logger.info(f"Add order to repo {order}")
        self.session.add(order)
        self.session.commit()

    def get(self, order_id):
        try:
            order = self.session.query(Order).filter_by(id=order_id).one()
        except sqlalchemy.orm.exc.NoResultFound:
            return None
        logger.debug(f"Get order from repo {order}")
        return order

    def list(self):
        orders = self.session.query(Order)
        if orders:
            logger.debug(f"Get orders from repo {orders}")
            return orders.all()
        return None

    def execute(self, statement, params=None):
        if params:
            return self.session.execute(statement, params)
        return self.session.execute(statement)


class FakeRepository(AbstractRepository):
    def __init__(self, orders):
        self._orders = set(orders)

    def add(self, order):
        self._orders.add(order)

    def get(self, order_id):
        return next(order for order in self._orders if order.id == order_id)

    def list(self):
        return list(self._orders)
