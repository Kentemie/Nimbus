from typing import Any

from domain.enums import OrderStatus
from domain.exceptions import RecordNotFoundException, OrderIsConfirmedException
from domain.models import Order as OrderModel, OrderProduct
from domain.schemas import Order as OrderSchema, OrderCreate, OrderUpdate, OrderFilter
from repositories.postgres import OrderDBRepository
from repositories.redis import OrderCacheRepository


class OrderService:
    def __init__(
        self,
        order_db_repository: OrderDBRepository,
        order_cache_repository: OrderCacheRepository,
    ):
        self.order_db_repository = order_db_repository
        self.order_cache_repository = order_cache_repository

    async def get_by_id(self, order_id: int) -> OrderSchema:
        cached_data = await self.order_cache_repository.get(order_id)
        if cached_data is not None:
            print("Got from cache")
            return OrderSchema(**cached_data)

        order_model = await self._fetch_order_or_raise(order_id)
        return await self._update_cache_and_serialize(order_model)

    async def get_filtered(
        self,
        user_id: int,
        order_filter: OrderFilter,
    ) -> list[OrderSchema]:
        order_models = await self.order_db_repository.get_filtered(
            user_id,
            order_filter,
        )
        return [OrderSchema.model_validate(om) for om in order_models]

    async def create(self, user_id: int, order_create: OrderCreate) -> OrderSchema:
        order_dict = order_create.get_create_update_dict()
        order_dict["user_id"] = user_id

        self._convert_order_products(order_dict)

        created_order_model = await self.order_db_repository.create(order_dict)
        return await self._update_cache_and_serialize(created_order_model)

    async def update(
        self,
        order_id: int,
        order_update: OrderUpdate,
    ) -> OrderSchema:
        order_model = await self._fetch_order_or_raise(order_id)
        if order_model.status == OrderStatus.CONFIRMED:
            raise OrderIsConfirmedException(order_model.id)

        order_dict = order_update.get_create_update_dict()
        self._convert_order_products(order_dict)

        updated_order_model = await self.order_db_repository.update(
            order_model, order_dict
        )
        return await self._update_cache_and_serialize(updated_order_model)

    async def soft_delete(self, order_id: int) -> None:
        await self.order_db_repository.soft_delete(order_id)
        await self.order_cache_repository.delete(order_id)

    async def hard_delete(self, order_id: int) -> None:
        await self.order_db_repository.hard_delete(order_id)
        await self.order_cache_repository.delete(order_id)

    async def _fetch_order_or_raise(self, order_id: int) -> OrderModel:
        order_model = await self.order_db_repository.get_by_id(order_id)
        if order_model is None:
            raise RecordNotFoundException(order_id)
        return order_model

    async def _update_cache_and_serialize(self, order_model: OrderModel) -> OrderSchema:
        print("Updating cache")
        order_schema = OrderSchema.model_validate(order_model)
        await self.order_cache_repository.set(
            order_schema.id, order_schema.model_dump()
        )
        return order_schema

    def _convert_order_products(self, data: dict[str, Any]) -> None:  # noqa
        """
        Проверяет наличие ключа 'order_products' в словаре и, если он есть,
        преобразует каждый элемент в экземпляр OrderProduct.
        """
        raw_order_products = data.pop("order_products", None)

        if raw_order_products and isinstance(raw_order_products, list):
            data["order_products"] = [OrderProduct(**rop) for rop in raw_order_products]
