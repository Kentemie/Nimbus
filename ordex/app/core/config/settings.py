from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

from .api import ApiConfig
from .app import AppConfig
from .database import DatabaseConfig
from .auth import AuthenticationConfig


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        extra="allow",
        case_sensitive=False,
        env_prefix="CONFIG__",
        env_file="ordex.env",
        env_nested_delimiter="__",
    )

    API: ApiConfig = ApiConfig()
    APP: AppConfig
    AUTH: AuthenticationConfig
    DATABASE: DatabaseConfig
