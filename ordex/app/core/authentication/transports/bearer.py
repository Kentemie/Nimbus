from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from .base import Transport

from domain.types import OpenAPIResponseType
from domain.exceptions import TransportLogoutNotSupportedException
from domain.schemas import BearerResponse
from core.config import settings


class BearerTransport(Transport):
    scheme: OAuth2PasswordBearer

    def __init__(self, token_url: str):
        self.scheme = OAuth2PasswordBearer(token_url, auto_error=False)

    async def get_login_response(self, token: str) -> Response:  # noqa
        bearer_response = BearerResponse(access_token=token, token_type="bearer")
        return JSONResponse(bearer_response.model_dump())

    async def get_logout_response(self) -> Response:
        raise TransportLogoutNotSupportedException()

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponse,
            },
        }

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {}


bearer_transport = BearerTransport(
    token_url=settings.API.BEARER_TOKEN_URL,
)
