from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.v1.common import ErrorModel, ErrorCode
from api.v1.dependencies import get_user_service
from domain.exceptions import RecordAlreadyExistsException, InvalidPasswordException
from domain.schemas import User as UserSchema, UserCreate

from services import UserService


def get_register_router(prefix: str, tags: list[str]) -> APIRouter:
    """
    Создаёт маршрутизатор для регистрации пользователей.

    :param prefix: Префикс URL для маршрутов регистрации.
    :param tags: Теги для классификации маршрутов регистрации в документации OpenAPI.
    :return: Настроенный маршрутизатор с эндпоинтом регистрации.
    """

    router = APIRouter(prefix=prefix, tags=tags)

    @router.post(
        "/register",
        response_model=UserSchema,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.RECORD_ALREADY_EXISTS: {
                                "summary": "Пользователь с такой электронной почтой уже существует.",
                                "value": {"detail": ErrorCode.RECORD_ALREADY_EXISTS},
                            },
                            ErrorCode.INVALID_PASSWORD: {
                                "summary": "Неправильный пароль.",
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
        summary="Эндпойнт для регистрации новых пользователей",
        name="register:register",
    )
    async def register(
        request: Request,
        user_service: Annotated["UserService", Depends(get_user_service)],
        user_create: UserCreate,
    ) -> UserSchema:
        """
        Обрабатывает запрос на регистрацию нового пользователя.

        :param request: HTTP-запрос, инициирующий регистрацию.
        :param user_create: Данные для создания нового пользователя.
        :param user_service: Сервис для работы с пользователями.
        :return: Зарегистрированный пользователь.
        :raises HTTPException: Если пользователь уже существует или пароль невалиден.
        """
        try:
            created_user = await user_service.create(user_create, request=request)
            return UserSchema.model_validate(created_user)
        except RecordAlreadyExistsException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RECORD_ALREADY_EXISTS,
            )
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

    return router
