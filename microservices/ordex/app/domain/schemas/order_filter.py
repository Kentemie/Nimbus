from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from domain.enums import OrderStatus


class OrderFilter(BaseModel):
    status: Optional[OrderStatus] = Field(
        None,
        description="Статус заказа",
        example=OrderStatus.PENDING,
    )
    min_price: Optional[float] = Field(
        None,
        gt=0,
        description="Минимальная цена",
        example=10.0,
    )
    max_price: Optional[float] = Field(
        None,
        gt=0,
        description="Максимальная цена",
        example=500.0,
    )

    model_config = ConfigDict(
        extra="forbid",
    )
