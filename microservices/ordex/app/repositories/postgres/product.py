from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.models import Product


class ProductRepository:
    """
    Репозиторий для работы с продуктами в базе данных PostgreSQL.

    :param session: Асинхронная сессия для работы с базой данных.

    Методы:
    - `get_by_id`: Получение продукта по ID.
    - `get_by_ids`: Получение списка продуктов по их идентификаторам.
    - `create`: Создание нового продукта.
    - `update`: Обновление существующего продукта.
    - `delete`: Удаление продукта.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Получает продукт по ID.

        :param product_id: Идентификатор продукта.
        :return: Модель продукта или None, если не найдено.
        """
        stmt = select(Product).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, product_ids: list[int]) -> list[Product]:
        """
        Получает список продуктов по их идентификаторам.

        :param product_ids: Список идентификаторов продуктов.
        :return: Список моделей продуктов.
        """
        stmt = select(Product).where(Product.id.in_(product_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, create_dict: dict[str, Any]) -> Product:
        """
        Создаёт новый продукт.

        :param create_dict: Данные для создания продукта.
        :return: Созданная модель продукта.
        """
        product = Product(**create_dict)

        self.session.add(product)

        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def update(self, product: Product, update_dict: dict[str, Any]) -> Product:
        """
        Обновляет существующий продукт.

        :param product: Модель продукта для обновления.
        :param update_dict: Данные для обновления продукта.
        :return: Обновлённая модель продукта.
        """
        for key, value in update_dict.items():
            setattr(product, key, value)

        self.session.add(product)

        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def delete(self, product: Product) -> None:
        """
        Удаляет продукт.

        :param product: Модель продукта для удаления.
        """
        await self.session.delete(product)
        await self.session.commit()
