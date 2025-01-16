from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from .base import Transport

from domain.types import OpenAPIResponseType
from domain.exceptions import TransportLogoutNotSupportedException
from domain.schemas import BearerResponse
from core.config import settings


class BearerTransport(Transport):
    """
    Реализует транспорт для работы с токенами Bearer.

    :param token_url: URL для получения токена.

    Методы:
    - `get_login_response`: Возвращает JSON с данными токена.
    - `get_logout_response`: Вызывает исключение, так как метод не поддерживается.
    - `get_openapi_login_responses_success`: Возвращает успешный ответ для OpenAPI документации.
    - `get_openapi_logout_responses_success`: Возвращает пустой успешный ответ для OpenAPI документации.
    """

    scheme: OAuth2PasswordBearer

    def __init__(self, token_url: str):
        self.scheme = OAuth2PasswordBearer(token_url, auto_error=False)

    async def get_login_response(self, token: str) -> Response:  # noqa
        """
        Возвращает JSON с данными токена.

        :param token: Bearer токен.
        :return: JSON ответ с токеном.
        """
        bearer_response = BearerResponse(access_token=token, token_type="bearer")
        return JSONResponse(bearer_response.model_dump())

    async def get_logout_response(self) -> Response:
        """
        Вызывает исключение, так как метод выхода не поддерживается.

        :raises TransportLogoutNotSupportedException: Метод не поддерживается.
        """
        raise TransportLogoutNotSupportedException()

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        """
        Возвращает успешный ответ для OpenAPI документации.

        :return: Ответ 200 OK для OpenAPI.
        """
        return {
            status.HTTP_200_OK: {
                "model": BearerResponse,
            },
        }

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        """
        Возвращает пустой успешный ответ для OpenAPI документации.

        :return: Пустой ответ 200 OK для OpenAPI.
        """
        return {}


bearer_transport = BearerTransport(
    token_url=settings.API.BEARER_TOKEN_URL,
)
