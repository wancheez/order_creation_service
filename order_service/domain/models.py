import json
from datetime import datetime
from typing import Optional


class User:
    resource_name = "users"

    def __init__(self, user_id: str, first_name: str, last_name: str):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def from_json(cls, user_dict: dict):
        try:
            result = cls(user_dict["id"], user_dict["firstName"], user_dict["lastName"])
        except KeyError as ex:
            raise ValueError(f"Field {ex} was not found in {user_dict}")
        return result

    def __eq__(self, other):
        return self.user_id == other.user_id

    def __str__(self):
        return json.dumps(
            {
                "user_id": self.user_id,
                "first_name": self.first_name,
                "last_name": self.last_name,
            }
        )


class Product:
    resource_name = "products"

    def __init__(self, code: str, name: str, price: float):
        self.code = code
        self.name = name
        self.price = price

    @classmethod
    def from_json(cls, product_dict: dict):
        try:
            result = cls(
                product_dict["code"], product_dict["name"], product_dict["price"]
            )
        except KeyError as ex:
            raise ValueError(f"Field {ex} not found in {product_dict}")
        return result

    def __eq__(self, other):
        return (
            self.code == other.code
            and self.name == other.name
            and self.price == other.price
        )

    def __str__(self):
        return json.dumps(
            {
                "code": self.code,
                "name": self.name,
                "price": self.price,
            }
        )


class Order:
    resource_name = "orders"

    def __init__(
        self,
        order_id: str,
        user: User,
        product: Product,
        created_at: Optional[datetime] = None,
    ):
        self.id = order_id
        self._user = user
        self._product = product
        if not created_at:
            self.created_at = datetime.now()
        else:
            self.created_at = created_at
        self.user_id = self._user.user_id
        self.product_code = self._product.code
        self.customer_fullname = f"{self._user.first_name} {self._user.last_name}"
        self.product_name = self._product.name
        self.total_amount = self._product.price

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def to_json(self):
        return {
            "id": self.id,
            "user_id": str(self.user_id),
            "product_code": str(self.product_code),
            "customer_fullname": str(self.customer_fullname),
            "product_name": str(self.product_name),
            "total_amount": str(self.total_amount),
        }

    def __str__(self):
        return json.dumps(self.to_json())
