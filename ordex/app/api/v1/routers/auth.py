from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from api.v1.common import ErrorModel, ErrorCode
from api.v1.dependencies import Authenticator, get_user_service
from core.authentication import AuthenticationBackend
from domain.schemas import User as UserSchema
from domain.types import OpenAPIResponseType
from services import UserService


def get_auth_router(
    prefix: str,
    tags: list[str],
    backend: AuthenticationBackend,
    authenticator: Authenticator,
    requires_verification: bool = False,
) -> APIRouter:
    """
    Создаёт и настраивает маршрутизатор для аутентификации с заданными параметрами.

    :param prefix: Префикс URL для всех маршрутов этого роутера.
    :param tags: Теги для классификации маршрутов в OpenAPI документации.
    :param backend: Бэкенд аутентификации, отвечающий за логику входа/выхода.
    :param authenticator: Объект, предоставляющий зависимость для получения текущего пользователя по JWT.
    :param requires_verification: Флаг, требующий верификации пользователя.
    :return: Настроенный маршрутизатор с маршрутами для login и logout.
    """

    router = APIRouter(prefix=prefix, tags=tags)

    # Получаем зависимость для текущего аутентифицированного пользователя на основе JWT.
    get_current_jwt_user = authenticator.current_jwt_user(
        is_active=True, is_verified=requires_verification
    )

    login_responses: OpenAPIResponseType = {
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Неверные учетные данные или пользователь неактивен.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        },
                        ErrorCode.USER_NOT_VERIFIED: {
                            "summary": "Пользователь не прошел верификацию.",
                            "value": {"detail": ErrorCode.USER_NOT_VERIFIED},
                        },
                    }
                }
            },
        },
        **backend.transport.get_openapi_login_responses_success(),
    }

    logout_responses: OpenAPIResponseType = {
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.MISSING_TOKEN: {
                            "summary": "Отсутствует токен или пользователь неактивен.",
                            "value": {"detail": ErrorCode.MISSING_TOKEN},
                        },
                    }
                }
            },
        },
        **backend.transport.get_openapi_logout_responses_success(),
    }

    @router.post(
        "/login",
        responses=login_responses,
        summary="Эндпоинт входа пользователя",
        description=(
            "Позволяет пользователю аутентифицироваться, проверяет учетные данные, "
            "активность и верификацию пользователя. Возвращает JWT токен при успешной аутентификации."
        ),
        name=f"auth:{backend.name}:login",
    )
    async def login(
        request: Request,
        user_service: Annotated[UserService, Depends(get_user_service)],
        credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    ):
        """
        Обрабатывает запрос на вход пользователя.

        :param request: HTTP-запрос.
        :param credentials: Форма с учетными данными пользователя.
        :param user_service: Сервис для работы с пользователями.
        :return: Ответ от backend.login с JWT токеном при успешной аутентификации.
        """
        user = await user_service.authenticate(credentials)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )

        if requires_verification and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.USER_NOT_VERIFIED,
            )

        response = await backend.login(UserSchema.model_validate(user))

        await user_service.on_after_login(user, request, response)

        return response

    @router.post(
        "/logout",
        responses=logout_responses,
        summary="Эндпоинт выхода пользователя",
        description=(
            "Позволяет пользователю завершить сеанс, отзывая JWT токен. "
            "Требует действительного токена в заголовке запроса."
        ),
        name=f"auth:{backend.name}:logout",
    )
    async def logout(
        user_token: Annotated[tuple[UserSchema, str], Depends(get_current_jwt_user)],
    ):
        """
        Обрабатывает запрос на выход пользователя.

        :param user_token: Кортеж, содержащий объект пользователя и JWT токен,
                           полученные из зависимости get_current_jwt_user.
        :return: Ответ от backend.logout, подтверждающий успешный выход.
        """
        _, token = user_token
        return await backend.logout(token)

    return router
