from typing import Optional, Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from domain.models import Order, OrderProduct as OrderProductModel
from domain.schemas import OrderFilter


class OrderRepository:
    """
    Репозиторий для работы с заказами в базе данных PostgreSQL.

    :param session: Асинхронная сессия для работы с базой данных.

    Методы:
    - `get_by_id`: Получение заказа по ID.
    - `get_filtered`: Получение заказов с фильтрацией.
    - `create`: Создание нового заказа.
    - `update`: Обновление существующего заказа.
    - `soft_delete`: Логическое удаление заказа.
    - `hard_delete`: Полное удаление заказа из базы данных.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        Получает заказ по ID.

        :param order_id: Идентификатор заказа.
        :return: Модель заказа или None, если не найдено.
        """
        stmt = (
            select(Order)
            .where(
                Order.id == order_id,
                Order.deleted_at.is_(None),
            )
            .options(
                selectinload(Order.order_products).joinedload(
                    OrderProductModel.product
                ),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_filtered(
        self,
        user_id: int,
        order_filter: OrderFilter,
    ) -> list[Order]:
        """
        Получает список заказов с фильтрацией.

        :param user_id: Идентификатор пользователя.
        :param order_filter: Параметры фильтрации.
        :return: Список моделей заказов.
        """
        stmt = select(Order).where(
            Order.user_id == user_id,
            Order.deleted_at.is_(None),
        )
        if order_filter.status:
            stmt = stmt.where(Order.status == order_filter.status)
        if order_filter.min_price is not None:
            stmt = stmt.where(Order.total_price >= order_filter.min_price)
        if order_filter.max_price is not None:
            stmt = stmt.where(Order.total_price <= order_filter.max_price)

        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def create(self, create_dict: dict[str, Any]) -> Order:
        """
        Создаёт новый заказ.

        :param create_dict: Данные для создания заказа.
        :return: Созданная модель заказа.
        """
        order = Order(**create_dict)

        self.session.add(order)

        await self.session.commit()
        await self.session.refresh(order)

        return order

    async def update(self, order: Order, update_dict: dict[str, Any]) -> None:
        """
        Обновляет существующий заказ.

        :param order: Модель заказа для обновления.
        :param update_dict: Данные для обновления заказа.
        """
        for key, value in update_dict.items():
            setattr(order, key, value)

        self.session.add(order)

        await self.session.commit()
        await self.session.refresh(order)

    async def soft_delete(self, order_id: int) -> None:
        """
        Логически удаляет заказ.

        :param order_id: Идентификатор заказа.
        """
        stmt = (
            update(Order)
            .where(Order.id == order_id)
            .values(deleted_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def hard_delete(self, order_id: int) -> None:
        """
        Полностью удаляет заказ.

        :param order_id: Идентификатор заказа.
        """
        stmt = delete(Order).where(Order.id == order_id)
        await self.session.execute(stmt)
        await self.session.commit()
