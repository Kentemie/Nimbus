from redis.asyncio import Redis
from redis.asyncio import BlockingConnectionPool


class RedisManager:
    """
    Управляет подключениями к Redis и выдачей клиентских объектов для различных баз данных.

    :param host: Хост Redis сервера (по умолчанию localhost).
    :param port: Порт Redis сервера (по умолчанию 6379).
    :param max_connections: Максимальное количество подключений (по умолчанию 100).
    :param timeout: Тайм-аут подключения (по умолчанию 10).

    Методы:
    - `get_stats_db`: Возвращает клиент для базы данных статистики.
    - `get_cache_db`: Возвращает клиент для базы данных кеша.
    - `close`: Закрывает пул подключений.
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
        """
        Возвращает клиент для работы с базой данных статистики.

        :return: Клиент Redis для базы данных статистики.
        """
        return self._db["stats"]

    def get_cache_db(self) -> Redis:
        """
        Возвращает клиент для работы с базой данных кеша.

        :return: Клиент Redis для базы данных кеша.
        """
        return self._db["cache"]

    async def close(self):
        """
        Закрывает пул подключений к Redis.
        """
        await self._connection_pool.aclose()
