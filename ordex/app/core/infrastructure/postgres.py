from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)


class PostgresManager:
    """
    Управляет подключением к PostgreSQL базе данных.

    :param url: URL подключения к базе данных.
    :param engine_kwargs: Дополнительные параметры для настройки движка SQLAlchemy.

    Методы:
    - `get_session`: Возвращает сессию для работы с базой данных.
    - `dispose`: Завершает все подключения.
    """

    def __init__(
        self,
        url: str,
        engine_kwargs: dict[str, Any],
    ) -> None:
        self._engine: AsyncEngine = create_async_engine(url, **engine_kwargs)
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Возвращает асинхронную сессию для работы с базой данных.

        :yield: Сессия AsyncSession.
        """
        async with self._session_factory() as session:
            yield session

    async def dispose(self, close: bool = True) -> None:
        """
        Завершает все подключения к базе данных.

        :param close: Закрыть ли активные подключения.
        """
        await self._engine.dispose(close)
