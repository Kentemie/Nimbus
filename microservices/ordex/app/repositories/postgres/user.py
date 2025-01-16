from typing import Optional, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.models import User


class UserRepository:
    """
    Репозиторий для работы с пользователями в базе данных PostgreSQL.

    :param session: Асинхронная сессия для работы с базой данных.

    Методы:
    - `get_by_id`: Получение пользователя по ID.
    - `get_by_email`: Получение пользователя по email.
    - `create`: Создание нового пользователя.
    - `update`: Обновление данных пользователя.
    - `delete`: Удаление пользователя.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Получает пользователя по ID.

        :param user_id: Идентификатор пользователя.
        :return: Модель пользователя или None, если не найден.
        """
        stmt = select(User).where(User.id == user_id).options(selectinload(User.roles))

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Получает пользователя по email.

        :param email: Email пользователя.
        :return: Модель пользователя или None, если не найден.
        """
        stmt = (
            select(User)
            .where(func.lower(User.email) == func.lower(email))  # type: ignore
            .options(selectinload(User.roles))
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def create(self, create_dict: dict[str, Any]) -> User:
        """
        Создаёт нового пользователя.

        :param create_dict: Данные для создания пользователя.
        :return: Созданная модель пользователя.
        """
        user = User(**create_dict)

        self.session.add(user)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def update(self, user: User, update_dict: dict[str, Any]) -> User:
        """
        Обновляет данные пользователя.

        :param user: Модель пользователя для обновления.
        :param update_dict: Данные для обновления пользователя.
        :return: Обновлённая модель пользователя.
        """
        for key, value in update_dict.items():
            setattr(user, key, value)

        self.session.add(user)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def delete(self, user: User) -> None:
        """
        Удаляет пользователя.

        :param user: Модель пользователя для удаления.
        """
        await self.session.delete(user)
        await self.session.commit()
