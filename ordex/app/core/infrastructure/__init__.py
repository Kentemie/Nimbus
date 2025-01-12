from .postgres import PostgresManager

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
