from redis.asyncio import Redis
from redis.asyncio import BlockingConnectionPool


class RedisManager:
    """
    Отвечает за создание и хранение пула подключений к Redis,
    а также выдачу клиентских объектов redis.asyncio.Redis на нужных db.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        max_connections: int = 100,
        timeout: int = 10,
    ):
        self._host = host
        self._port = port
        self._max_connections = max_connections
        self._timeout = timeout

        # Создаём общий пул подключений
        self._connection_pool = BlockingConnectionPool(
            host=self._host,
            port=self._port,
            max_connections=self._max_connections,
            timeout=self._timeout,
        )

        self._db = {
            "stats": Redis(connection_pool=self._connection_pool, db=0),
            "cache": Redis(connection_pool=self._connection_pool, db=1),
        }

    def get_stats_db(self) -> Redis:
        return self._db["stats"]

    def get_cache_db(self) -> Redis:
        return self._db["cache"]

    async def close(self):
        await self._connection_pool.aclose()
