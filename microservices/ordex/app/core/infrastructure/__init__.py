from .postgres import PostgresManager
from .redis import RedisManager
from .kafka import KafkaManager

from core.config import settings

postgres_manager = PostgresManager(
    url=str(settings.DATABASE.URL),
    engine_kwargs={
        "echo": settings.APP.ENVIRONMENT == "staging",
        "echo_pool": settings.APP.ENVIRONMENT == "staging",
        "pool_size": settings.DATABASE.POOL_SIZE,
        "max_overflow": settings.DATABASE.MAX_OVERFLOW,
    },
)

redis_manager = RedisManager(
    host=settings.REDIS.HOST,
    port=settings.REDIS.PORT,
    max_connections=settings.REDIS.MAX_CONNECTIONS,
    timeout=settings.REDIS.TIMEOUT,
)

kafka_manager = KafkaManager(
    bootstrap_servers=settings.KAFKA.BOOTSTRAP_SERVERS,
    topic=settings.KAFKA.TOPIC,
)
