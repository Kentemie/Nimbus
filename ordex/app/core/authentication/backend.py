from typing import TYPE_CHECKING

from fastapi import Response, status

from core.authentication.strategies import Strategy
from core.authentication.transports import Transport
from domain.exceptions import (
    StrategyDestroyTokenNotSupportedException,
    TransportLogoutNotSupportedException,
)


if TYPE_CHECKING:
    from domain.models import User


class AuthenticationBackend:
    name: str

    def __init__(
        self,
        name: str,
        transport: Transport,
        strategy: Strategy,
    ):
        self.name = name
        self.transport = transport
        self.strategy = strategy

    async def login(self, user: "User") -> Response:
        token = await self.strategy.write_token(user)
        return await self.transport.get_login_response(token)

    async def logout(self, token: str) -> Response:
        try:
            await self.strategy.destroy_token(token)
        except StrategyDestroyTokenNotSupportedException:
            pass

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedException:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response
