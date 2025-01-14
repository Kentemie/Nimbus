from typing import Any

from domain.enums import OrderStatus
from domain.exceptions import RecordNotFoundException, OrderIsConfirmedException
from domain.models import Order as OrderModel, OrderProduct
from domain.schemas import OrderCreate, OrderUpdate, OrderFilter
from repositories.postgres import OrderRepository


class OrderService:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def get_by_id(self, order_id: int) -> OrderModel:
        order = await self.order_repository.get_by_id(order_id)

        if order is None:
            raise RecordNotFoundException(order_id)

        return order

    async def get_filtered(
        self,
        user_id: int,
        order_filter: OrderFilter,
    ) -> list[OrderModel]:
        return await self.order_repository.get_filtered(user_id, order_filter)

    async def create(self, user_id: int, order_create: OrderCreate) -> OrderModel:
        order_dict = order_create.get_create_update_dict()
        order_dict["user_id"] = user_id

        self._convert_order_products(order_dict)

        return await self.order_repository.create(order_dict)

    async def update(self, order_update: OrderUpdate, order: OrderModel) -> OrderModel:
        if order.status == OrderStatus.CONFIRMED:
            raise OrderIsConfirmedException(order.id)

        order_dict = order_update.get_create_update_dict()

        self._convert_order_products(order_dict)

        return await self.order_repository.update(order, order_dict)

    async def soft_delete(self, order: OrderModel) -> None:
        await self.order_repository.soft_delete(order)

    async def hard_delete(self, order: OrderModel) -> None:
        await self.order_repository.hard_delete(order)

    def _convert_order_products(self, data: dict[str, Any]) -> None:  # noqa
        """
        Проверяет наличие ключа 'order_products' в словаре и, если он есть,
        преобразует каждый элемент в экземпляр OrderProduct.
        """
        raw_order_products = data.pop("order_products", None)

        if raw_order_products and isinstance(raw_order_products, list):
            data["order_products"] = [OrderProduct(**rop) for rop in raw_order_products]
