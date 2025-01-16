from pydantic import BaseModel


class RedisConfig(BaseModel):
    HOST: str
    PORT: int
    MAX_CONNECTIONS: int
    TIMEOUT: int
    STATS_DB: int
    CACHE_DB: int
