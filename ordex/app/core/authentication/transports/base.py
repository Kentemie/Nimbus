from typing import Protocol

from fastapi.openapi.models import Response
from fastapi.security.base import SecurityBase

from domain.types import OpenAPIResponseType


class Transport(Protocol):
    scheme: SecurityBase

    async def get_login_response(self, token: str) -> Response: ...

    async def get_logout_response(self) -> Response: ...

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType: ...

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType: ...
