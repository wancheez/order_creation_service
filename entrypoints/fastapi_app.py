import aiohttp.client_exceptions
import fastapi.exceptions
from fastapi import FastAPI, Response
from prometheus_client import REGISTRY
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel

from order_service.dependency.injector import DependencyInjector
from order_service.service_layer.services import get_order, get_orders, send_order

DependencyInjector()
app = FastAPI()


class CreateRequestParams(BaseModel):
    user_id: str
    product_code: str


@app.post("/order")
async def create_order_endpoint(item: CreateRequestParams):
    """Create an order.

    Args:
        item: User and Product
    """
    try:
        order_id = await send_order(item.user_id, item.product_code)
    except aiohttp.client_exceptions.ClientResponseError as ex:
        exception_info = f"{ex.message} {ex.request_info.url.raw_path}"
        raise fastapi.exceptions.HTTPException(
            status_code=ex.status,
            detail=exception_info,
        )
    return order_id


@app.get("/order/{order_id}")
async def get_order_endpoint(order_id: str):
    """Get an order by id.

    Args:
        order_id: Order id

    Returns:
        Order information
    """
    order = await get_order(order_id)
    if not order:
        raise fastapi.exceptions.HTTPException(status_code=404)
    return order.to_json()


@app.get("/orders")
async def get_order_endpoint():
    """Get all orders.

    Returns:
        Orders information
    """
    orders = await get_orders()
    if not orders:
        raise fastapi.exceptions.HTTPException(status_code=404)
    return [order.to_json() for order in orders]


@app.get('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), headers={"Content-Type": CONTENT_TYPE_LATEST})
