from sqlalchemy import Column, Date, Float, String, Table
from sqlalchemy.orm import registry

from order_service.domain.models import Order

mapper_registry = registry()

orders = Table(
    "orders",
    mapper_registry.metadata,
    Column("id", String(255), primary_key=True),
    Column("user_id", String(255), nullable=False),
    Column("product_code", String(255), nullable=False),
    Column("customer_fullname", String(255), nullable=False),
    Column("product_name", String(255), nullable=False),
    Column("total_amount", Float(), nullable=False),
    Column("created_at", Date(), nullable=True),
)


def start_mappers():
    mapper_registry.map_imperatively(
        Order,
        orders,
    )
