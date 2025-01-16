import json
from typing import Any

from redis.asyncio import Redis


class CacheRepository:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def get(self, prefix: str, identifier: str | int) -> dict[str, Any] | None:
        key = self._generate_key(prefix, identifier)
        data = await self._redis.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set(
        self, prefix: str, identifier: str | int, data: dict[str, Any]
    ) -> None:
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
        return f"{prefix}:{identifier}"
