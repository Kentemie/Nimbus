import json
from typing import Any

from redis.asyncio import Redis


class CacheRepository:
    """
    Репозиторий для работы с кешем в Redis.

    :param redis: Объект Redis для взаимодействия с базой данных.

    Методы:
    - `get`: Получение данных из кеша.
    - `set`: Сохранение данных в кеш.
    - `delete`: Удаление данных из кеша.
    """

    def __init__(self, redis: Redis):
        self._redis = redis

    async def get(self, prefix: str, identifier: str | int) -> dict[str, Any] | None:
        """
        Получает данные из кеша по ключу.

        :param prefix: Префикс ключа.
        :param identifier: Идентификатор для генерации ключа.
        :return: Данные из кеша или None, если ключ не найден.
        """
        key = self._generate_key(prefix, identifier)
        data = await self._redis.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set(
        self, prefix: str, identifier: str | int, data: dict[str, Any]
    ) -> None:
        """
        Сохраняет данные в кеш.

        :param prefix: Префикс ключа.
        :param identifier: Идентификатор для генерации ключа.
        :param data: Данные для сохранения.
        """
        key = self._generate_key(prefix, identifier)
        await self._redis.set(key, json.dumps(data))

    async def delete(self, prefix: str, identifier: str | int) -> None:
        """
        Удаляет данные из кеша по ключу.

        :param prefix: Префикс ключа.
        :param identifier: Идентификатор для генерации ключа.
        """
        key = self._generate_key(prefix, identifier)
        await self._redis.delete(key)

    def _generate_key(self, prefix: str, identifier: str | int) -> str:  # noqa
        """
        Генерирует ключ для сохранения или извлечения данных из кеша.

        :param prefix: Префикс ключа.
        :param identifier: Идентификатор для генерации ключа.
        :return: Сгенерированный ключ.
        """
        return f"{prefix}:{identifier}"
