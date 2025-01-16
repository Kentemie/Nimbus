from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import EmailStr

from api.v1.common import ErrorModel, ErrorCode
from api.v1.dependencies import get_user_service
from domain.exceptions import (
    RecordNotFoundException,
    UserInactiveException,
    InvalidResetPasswordTokenException,
    InvalidPasswordException,
)
from services import UserService


def get_reset_password_router(prefix: str, tags: list[str]) -> APIRouter:
    """
    Создаёт маршрутизатор для обработки запросов на сброс пароля.

    :param prefix: Префикс URL для маршрутов сброса пароля.
    :param tags: Теги для классификации маршрутов в документации OpenAPI.
    :return: Настроенный маршрутизатор с эндпоинтами для восстановления и сброса пароля.
    """

    router = APIRouter(prefix=prefix, tags=tags)

    @router.post(
        "/forgot-password",
        status_code=status.HTTP_202_ACCEPTED,
        summary="Запрос на восстановление пароля",
        name="reset:forgot_password",
    )
    async def forgot_password(
        request: Request,
        user_service: Annotated["UserService", Depends(get_user_service)],
        email: EmailStr = Body(..., embed=True),
    ):
        """
        Обрабатывает запрос на восстановление пароля (Forgot Password).

        :param request: HTTP-запрос, инициирующий процесс восстановления пароля.
        :param user_service: Сервис для работы с пользователями.
        :param email: Электронная почта пользователя.
        :return: Всегда возвращает None, так как ответ не содержит данных.
        """
        try:
            user = await user_service.get_by_email(email)
        except RecordNotFoundException:
            return None

        try:
            await user_service.forgot_password(user, request)
        except (UserInactiveException, NotImplementedError):
            pass

        return None

    @router.post(
        "/reset-password",
        summary="Сброс пароля по токену",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.RESET_PASSWORD_BAD_TOKEN: {
                                "summary": "Неверный или просроченный токен.",
                                "value": {"detail": ErrorCode.RESET_PASSWORD_BAD_TOKEN},
                            },
                            ErrorCode.INVALID_PASSWORD: {
                                "summary": "Не удалось пройти валидацию пароля.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.INVALID_PASSWORD,
                                        "reason": (
                                            "Пароль слишком простой. Используйте как минимум 12 символов, "
                                            "большие и маленькие буквы, цифры и специальные символы."
                                        ),
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
        name="reset:reset_password",
    )
    async def reset_password(
        request: Request,
        user_service: Annotated["UserService", Depends(get_user_service)],
        token: str = Body(...),
        password: str = Body(...),
    ):
        """
        Обрабатывает запрос на сброс пароля с использованием токена.

        :param request: HTTP-запрос, инициирующий сброс пароля.
        :param user_service: Сервис для работы с пользователями.
        :param token: Токен сброса пароля.
        :param password: Новый пароль.
        :raises HTTPException: При неверном или просроченном токене,
                               неверном пароле или других ошибках.
        """
        try:
            await user_service.reset_password(token, password, request)
        except (
            InvalidResetPasswordTokenException,
            RecordNotFoundException,
            UserInactiveException,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        except NotImplementedError:
            pass

    return router
