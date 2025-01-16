from pydantic import BaseModel, SecretStr


class JWTStrategyConfig(BaseModel):
    SECRET_KEY: SecretStr
    PUBLIC_KEY: SecretStr
    ALGORITHM: str
    LIFETIME: int
    AUDIENCE: list[str]


class AuthenticationConfig(BaseModel):
    JWT_STRATEGY: JWTStrategyConfig
