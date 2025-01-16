from typing import Literal

from pydantic import BaseModel


class AppConfig(BaseModel):
    HOST: str
    PORT: int

    ENVIRONMENT: Literal["staging", "production"] = "staging"
    LOGS_DIR: str = "logs"
