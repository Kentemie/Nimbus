import logging

from typing import Any

from domain.enums import OrderStatus
from domain.exceptions import RecordNotFoundException, OrderIsConfirmedException
from domain.models import Order as OrderModel, OrderProduct
from domain.schemas import Order as OrderSchema, OrderCreate, OrderUpdate, OrderFilter
from repositories.postgres import OrderRepository
from repositories.redis import CacheRepository
from events import send_order_status_update_event


logger = logging.getLogger()

CACHE_PREFIX = "order"


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        cache_repository: CacheRepository,
    ):
        self.order_repository = order_repository
        self.cache_repository = cache_repository

    async def get_by_id(self, order_id: int) -> OrderSchema:
        logger.info("Fetching order with ID: %s", order_id)
        cached_data = await self.cache_repository.get(CACHE_PREFIX, order_id)
        if cached_data is not None:
            logger.info("Order with ID: %s found in cache", order_id)
            return OrderSchema(**cached_data)

        logger.info("Order with ID: %s not found in cache. Fetching from DB.", order_id)
        order_model = await self._fetch_order_or_raise(order_id)
        return await self._update_cache_and_serialize(order_model)

    async def get_filtered(
        self,
        user_id: int,
        order_filter: OrderFilter,
    ) -> list[OrderSchema]:
        logger.info(
            "Fetching orders for user ID: %s with filters: %s",
            user_id,
            order_filter,
        )
        order_models = await self.order_repository.get_filtered(
            user_id,
            order_filter,
        )
        return [OrderSchema.model_validate(om) for om in order_models]

    async def create(self, user_id: int, order_create: OrderCreate) -> OrderSchema:
        logger.info("Creating new order for user ID: %s", user_id)
        order_dict = order_create.get_create_update_dict()
        order_dict["user_id"] = user_id

        self._convert_order_products(order_dict)

        created_order_model = await self.order_repository.create(order_dict)
        logger.info("Order created with ID: %s", created_order_model.id)
        return await self._update_cache_and_serialize(created_order_model)

    async def update(
        self,
        order_id: int,
        order_update: OrderUpdate,
    ) -> OrderSchema:
        logger.info("Updating order with ID: %s", order_id)
        order_model = await self._fetch_order_or_raise(order_id)
        if order_model.status == OrderStatus.CONFIRMED:
            logger.warning(
                "Order with ID: %s is already confirmed. Update aborted.",
                order_id,
            )
            raise OrderIsConfirmedException(order_model.id)

        original_status = order_model.status

        order_dict = order_update.get_create_update_dict()
        self._convert_order_products(order_dict)

        await self.order_repository.update(order_model, order_dict)

        updated_status = order_model.status

        if original_status != updated_status:
            logger.info(
                "Order status changed for ID: %s from %s to %s. Emitting status update event.",
                order_id,
                original_status,
                updated_status,
            )

            await send_order_status_update_event(
                order_id,
                original_status,
                updated_status,
            )

        logger.info("Order with ID: %s updated successfully.", order_id)
        return await self._update_cache_and_serialize(order_model)

    async def soft_delete(self, order_id: int) -> None:
        logger.info("Soft deleting order with ID: %s", order_id)
        await self.order_repository.soft_delete(order_id)
        await self.cache_repository.delete(order_id)
        logger.info("Order with ID: %s soft deleted.", order_id)

    async def hard_delete(self, order_id: int) -> None:
        logger.info("Hard deleting order with ID: %s", order_id)
        await self.order_repository.hard_delete(order_id)
        await self.cache_repository.delete(order_id)
        logger.info("Order with ID: %s hard deleted.", order_id)

    async def _fetch_order_or_raise(self, order_id: int) -> OrderModel:
        logger.info("Fetching order from DB with ID: %s", order_id)
        order_model = await self.order_repository.get_by_id(order_id)
        if order_model is None:
            logger.warning("Order with ID: %s not found in DB.", order_id)
            raise RecordNotFoundException(order_id)
        return order_model

    async def _update_cache_and_serialize(self, order_model: OrderModel) -> OrderSchema:
        logger.info("Updating cache for order ID: %s", order_model.id)
        order_schema = OrderSchema.model_validate(order_model)
        await self.cache_repository.set(
            CACHE_PREFIX,
            order_schema.id,
            order_schema.model_dump(),
        )
        logger.info("Cache updated for order ID: %s", order_schema.id)
        return order_schema

    def _convert_order_products(self, data: dict[str, Any]) -> None:  # noqa
        """
        Проверяет наличие ключа 'order_products' в словаре и, если он есть,
        преобразует каждый элемент в экземпляр OrderProduct.
        """
        raw_order_products = data.pop("order_products", None)

        if raw_order_products and isinstance(raw_order_products, list):
            data["order_products"] = [OrderProduct(**rop) for rop in raw_order_products]
