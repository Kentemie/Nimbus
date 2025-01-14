from typing import Optional
from datetime import timezone, datetime, timedelta

import jwt

from pydantic import SecretStr
from pydantic import ValidationError

from .base import Strategy

from domain.exceptions import JWTStrategyDestroyTokenNotSupportedException
from domain.models import User as UserModel
from domain.schemas import User as UserSchema
from utils import encode_jwt, decode_jwt
from core.config import settings


class JWTStrategy(Strategy):
    def __init__(
        self,
        secret_key: SecretStr,
        public_key: SecretStr,
        algorithm: str = "HS256",
        lifetime: int = 3600,
        audience: list[str] = None,
    ):
        self.secret_key = secret_key
        self.public_key = public_key
        self.algorithm = algorithm
        self.lifetime = lifetime

        if not audience:
            self.audience = ["nimbus:auth"]

        self.audience = audience

    async def write_token(self, user_model: UserModel) -> str:
        user_schema = UserSchema.model_validate(user_model)
        payload = {
            "sub": f"{user_model.id}:{user_model.email}",
            "aud": self.audience,
            "iat": datetime.now(timezone.utc),
            "user": user_schema.model_dump(),
        }

        if self.lifetime:
            expire = datetime.now(timezone.utc) + timedelta(seconds=self.lifetime)
            payload["exp"] = expire

        return encode_jwt(payload, self.secret_key, self.algorithm)

    async def read_token(self, token: Optional[str]) -> Optional[UserSchema]:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token, self.secret_key, self.audience, algorithms=[self.algorithm]
            )

            user = data.get("user")
            if user is None:
                return None

            try:
                user_schema = UserSchema.model_validate(user)
                return user_schema
            except ValidationError as _:
                return None

        except jwt.PyJWTError:
            return None

    async def destroy_token(self, token: str) -> None:
        raise JWTStrategyDestroyTokenNotSupportedException()


jwt_strategy = JWTStrategy(
    secret_key=settings.AUTH.JWT_STRATEGY.SECRET_KEY,
    public_key=settings.AUTH.JWT_STRATEGY.PUBLIC_KEY,
    algorithm=settings.AUTH.JWT_STRATEGY.ALGORITHM,
    lifetime=settings.AUTH.JWT_STRATEGY.LIFETIME,
    audience=settings.AUTH.JWT_STRATEGY.AUDIENCE,
)
