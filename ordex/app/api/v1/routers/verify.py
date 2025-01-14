from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import EmailStr

from api.v1.common import ErrorModel, ErrorCode
from api.v1.dependencies import get_user_service

from domain.exceptions import (
    RecordNotFoundException,
    UserInactiveException,
    UserAlreadyVerifiedException,
    InvalidVerifyTokenException,
)
from domain.schemas import User
from services import UserService


def get_verify_router(prefix: str, tags: list[str]) -> APIRouter:
    """
    Создаёт маршрутизатор для верификации пользователей.

    :param prefix: Префикс URL для маршрутов верификации.
    :param tags: Теги для классификации маршрутов в документации OpenAPI.
    :return: Настроенный маршрутизатор с эндпоинтами запроса токена верификации и верификации.
    """

    router = APIRouter(prefix=prefix, tags=tags)

    @router.post(
        "/request-verify-token",
        status_code=status.HTTP_202_ACCEPTED,
        summary="Запрос токена верификации пользователя",
        name="verify:request-token",
    )
    async def request_verify_token(
        request: Request,
        user_service: Annotated[UserService, Depends(get_user_service)],
        email: EmailStr = Body(..., embed=True),
    ):
        """
        Обрабатывает запрос на получение токена верификации для пользователя.

        :param request: HTTP-запрос, инициирующий процесс верификации.
        :param user_service: Сервис для работы с пользователями.
        :param email: Электронная почта пользователя.
        :return: Всегда возвращает None.
        """
        try:
            user = await user_service.get_by_email(email)
            await user_service.request_verify(user, request)
        except (
            RecordNotFoundException,
            UserInactiveException,
            UserAlreadyVerifiedException,
            NotImplementedError,
        ):
            pass

        return None

    @router.post(
        "/verify",
        response_model=User,
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.VERIFY_USER_BAD_TOKEN: {
                                "summary": "Неверный токен, несуществующий пользователь или "
                                "не тот e-mail, который установлен для пользователя.",
                                "value": {"detail": ErrorCode.VERIFY_USER_BAD_TOKEN},
                            },
                            ErrorCode.USER_ALREADY_VERIFIED: {
                                "summary": "Пользователь уже верифицирован.",
                                "value": {"detail": ErrorCode.USER_ALREADY_VERIFIED},
                            },
                        }
                    }
                },
            }
        },
        name="verify:verify",
    )
    async def verify(
        request: Request,
        user_service: Annotated[UserService, Depends(get_user_service)],
        token: str = Body(..., embed=True),
    ):
        """
        Обрабатывает запрос на верификацию пользователя по токену.

        :param request: HTTP-запрос, инициирующий верификацию.
        :param user_service: Сервис для работы с пользователями.
        :param token: Токен верификации.
        :return: Верифицированный пользователь.
        :raises HTTPException: При неверном токене или если пользователь уже верифицирован.
        """
        try:
            user = await user_service.verify(token, request)
            return User.model_validate(user)
        except (InvalidVerifyTokenException, RecordNotFoundException):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )
        except UserAlreadyVerifiedException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.USER_ALREADY_VERIFIED,
            )
        except NotImplementedError:
            pass

    return router
