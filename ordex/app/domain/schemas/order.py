from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator, Field

from .product import Product
from domain.enums import OrderStatus


class CreateUpdateDictModel(BaseModel):
    def get_create_update_dict(self):
        return self.model_dump(
            exclude_unset=True,
            exclude={
                "id",
                "deleted_at",
            },
        )


class OrderProduct(BaseModel):
    product: Product = Field(..., example={"id": 1, "name": "Продукт", "price": 100.0})
    quantity: int = Field(..., example=2)

    model_config = ConfigDict(from_attributes=True)


class OrderProductCreateUpdate(BaseModel):
    product_id: int = Field(..., example=1)
    quantity: int = Field(..., example=2)


class Order(CreateUpdateDictModel):
    id: int = Field(..., example=123)
    user_id: int = Field(..., example=456)
    status: OrderStatus = Field(..., example=OrderStatus.PENDING)
    total_price: float = Field(..., example=299.99)
    deleted_at: Optional[datetime] = Field(None, example="2023-01-01T12:00:00")
    order_products: Optional[list[OrderProduct]] = Field(
        None,
        example=[
            {"product": {"id": 1, "name": "Продукт", "price": 100.0}, "quantity": 2}
        ],
    )

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(CreateUpdateDictModel):
    total_price: float = Field(..., example=299.99)
    order_products: list[OrderProductCreateUpdate] = Field(
        ..., example=[{"product_id": 1, "quantity": 2}]
    )


class OrderUpdate(CreateUpdateDictModel):
    status: Optional[OrderStatus] = Field(None, example=OrderStatus.CANCELLED)
    total_price: Optional[float] = Field(None, example=299.99)
    order_products: Optional[list[OrderProductCreateUpdate]] = Field(
        None, example=[{"product_id": 1, "quantity": 2}]
    )

    @model_validator(mode="before")
    @classmethod
    def check_total_price_and_order_products(cls, values):
        order_products = values.get("order_products")
        total_price = values.get("total_price")

        # Если одно из полей передано без другого — возбуждаем ошибку
        if (order_products is not None and total_price is None) or (
            total_price is not None and order_products is None
        ):
            raise ValueError(
                "Если передаётся одно из полей 'order_products' или 'total_price', "
                "должно передаваться и другое."
            )

        return values
