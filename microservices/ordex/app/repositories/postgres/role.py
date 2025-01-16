from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.models import Role


class RoleRepository:
    """
    Репозиторий для работы с ролями в базе данных PostgreSQL.

    :param session: Асинхронная сессия для работы с базой данных.

    Методы:
    - `get_by_id`: Получение роли по ID.
    - `get_by_ids`: Получение списка ролей по их идентификаторам.
    - `get_by_slug`: Получение роли по её слагу.
    - `create`: Создание новой роли.
    - `update`: Обновление существующей роли.
    - `delete`: Удаление роли.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        """
        Получает роль по ID.

        :param role_id: Идентификатор роли.
        :return: Модель роли или None, если не найдена.
        """
        stmt = select(Role).where(Role.id == role_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, role_ids: list[int]) -> list[Role]:
        """
        Получает список ролей по их идентификаторам.

        :param role_ids: Список идентификаторов ролей.
        :return: Список моделей ролей.
        """
        stmt = select(Role).where(Role.id.in_(role_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Optional[Role]:
        """
        Получает роль по слагу.

        :param slug: Слаг роли.
        :return: Модель роли или None, если не найдена.
        """
        stmt = select(Role).where(Role.slug == slug)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create(self, create_dict: dict[str, Any]) -> Role:
        """
        Создаёт новую роль.

        :param create_dict: Данные для создания роли.
        :return: Созданная модель роли.
        """
        role = Role(**create_dict)

        self.session.add(role)

        await self.session.commit()
        await self.session.refresh(role)

        return role

    async def update(self, role: Role, update_dict: dict[str, Any]) -> Role:
        """
        Обновляет существующую роль.

        :param role: Модель роли для обновления.
        :param update_dict: Данные для обновления роли.
        :return: Обновлённая модель роли.
        """
        for key, value in update_dict.items():
            setattr(role, key, value)

        self.session.add(role)

        await self.session.commit()
        await self.session.refresh(role)

        return role

    async def delete(self, role: Role) -> None:
        """
        Удаляет роль.

        :param role: Модель роли для удаления.
        """
        await self.session.delete(role)
        await self.session.commit()
