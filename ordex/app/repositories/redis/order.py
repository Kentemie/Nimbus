import json
from typing import Any

from redis.asyncio import Redis


class OrderCacheRepository:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def get(self, order_id: int) -> dict[str, Any] | None:
        key = self._generate_key(order_id)
        data = await self._redis.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set(self, order_id: int, data: dict[str, Any]) -> None:
        key = self._generate_key(order_id)
        await self._redis.set(key, json.dumps(data))

    async def delete(self, order_id: int) -> None:
        key = self._generate_key(order_id)
        await self._redis.delete(key)

    def _generate_key(self, order_id: int) -> str:  # noqa
        return f"order:{order_id}"
