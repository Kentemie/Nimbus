from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from api.v1.common import (
    ErrorModel,
    ErrorCode,
    unauthorized_response,
    forbidden_response,
)
from api.v1.dependencies import Authenticator, get_user_service

from domain.exceptions import (
    RecordNotFoundException,
    RecordAlreadyExistsException,
    InvalidPasswordException,
)
from domain.schemas import User as UserSchema, UserUpdate
from domain.models import User as UserModel
from domain.types import OpenAPIResponseType
from services import UserService


def get_users_router(
    prefix: str,
    tags: list[str],
    authenticator: Authenticator,
    requires_verification: bool = False,
) -> APIRouter:
    """
    Создаёт маршрутизатор для управления пользователями.

    :param prefix: Префикс URL для маршрутов управления пользователями.
    :param tags: Теги для классификации маршрутов в документации OpenAPI.
    :param authenticator: Объект аутентификатора для защиты эндпоинтов.
    :param requires_verification: Флаг, требующий верификации пользователя.
    :return: Настроенный маршрутизатор с CRUD-эндпоинтами для пользователей.
    """

    router = APIRouter(prefix=prefix, tags=tags)

    update_bad_response: OpenAPIResponseType = {
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
                                    "reason": "Пароль слишком простой. Используйте как минимум 12 символов, "
                                    "большие и маленькие буквы, цифры и специальные символы.",
                                }
                            },
                        },
                    }
                }
            },
        },
    }

    not_found_response: OpenAPIResponseType = {
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.RECORD_NOT_FOUND: {
                            "summary": "Пользователь не существует.",
                            "value": {"detail": ErrorCode.RECORD_NOT_FOUND},
                        },
                    }
                }
            },
        }
    }

    get_current_jwt_admin_user = authenticator.current_jwt_user(
        is_active=True, is_verified=requires_verification, required_roles=["admin"]
    )

    get_current_db_user = authenticator.current_db_user(
        is_active=True, is_verified=requires_verification
    )

    async def get_user_or_404(
        user_service: Annotated[UserService, Depends(get_user_service)],
        user_id: int,
    ) -> UserModel:
        try:
            return await user_service.get_by_id(user_id)
        except RecordNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    @router.get(
        "/me",
        response_model=UserSchema,
        status_code=status.HTTP_200_OK,
        responses={
            **unauthorized_response,
        },
        summary="Получить информацию о текущем пользователе",
        name="users:get_current_user",
    )
    async def get_me(
        user: Annotated[UserModel, Depends(get_current_db_user)],
    ):
        """
        Возвращает информацию о текущем аутентифицированном пользователе.
        """
        return UserSchema.model_validate(user)

    @router.patch(
        "/me",
        response_model=UserSchema,
        status_code=status.HTTP_200_OK,
        responses={
            **update_bad_response,
            **unauthorized_response,
        },
        summary="Обновить данные текущего пользователя",
        name="users:patch_current_user",
    )
    async def update_me(
        request: Request,
        user_service: Annotated[UserService, Depends(get_user_service)],
        user: Annotated[UserModel, Depends(get_current_db_user)],
        user_update: UserUpdate,
    ):
        """
        Обновляет данные текущего пользователя.

        :param request: HTTP-запрос.
        :param user_update: Данные для обновления пользователя.
        :param user: Текущий пользователь из базы данных.
        :param user_service: Сервис для работы с пользователями.
        :return: Обновлённая информация о пользователе.
        """
        try:
            updated_user = await user_service.update(user_update, user, request=request)
            return UserSchema.model_validate(updated_user)
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        except RecordAlreadyExistsException:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RECORD_ALREADY_EXISTS,
            )

    @router.get(
        "/{user_id}",
        response_model=UserSchema,
        status_code=status.HTTP_200_OK,
        responses={
            **unauthorized_response,
            **forbidden_response,
            **not_found_response,
        },
        dependencies=[Depends(get_current_jwt_admin_user)],
        summary="Получить информацию о пользователе по ID",
        name="users:get_user",
    )
    async def get_user(
        user: Annotated[UserModel, Depends(get_user_or_404)],
    ):
        """
        Возвращает информацию о пользователе по заданному идентификатору.
        """
        return UserSchema.model_validate(user)

    @router.patch(
        "/{user_id}",
        response_model=UserSchema,
        status_code=status.HTTP_200_OK,
        responses={
            **update_bad_response,
            **unauthorized_response,
            **forbidden_response,
            **not_found_response,
        },
        dependencies=[Depends(get_current_jwt_admin_user)],
        summary="Обновить данные пользователя по ID",
        name="users:patch_user",
    )
    async def update_user(
        request: Request,
        user_service: Annotated[UserService, Depends(get_user_service)],
        user: Annotated[UserModel, Depends(get_user_or_404)],
        user_update: UserUpdate,
    ):
        """
        Обновляет данные пользователя по заданному идентификатору.

        :param request: HTTP-запрос.
        :param user_update: Данные для обновления пользователя.
        :param user: Пользователь, найденный по ID.
        :param user_service: Сервис для работы с пользователями.
        :return: Обновлённая информация о пользователе.
        """
        try:
            updated_user = await user_service.update(user_update, user, request=request)
            return UserSchema.model_validate(updated_user)
        except InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        except RecordAlreadyExistsException:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RECORD_ALREADY_EXISTS,
            )

    @router.delete(
        "/{user_id}",
        response_class=Response,
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            **unauthorized_response,
            **forbidden_response,
            **not_found_response,
        },
        dependencies=[Depends(get_current_jwt_admin_user)],
        summary="Удалить пользователя по ID",
        name="users:delete_user",
    )
    async def delete_user(
        request: Request,
        user_service: Annotated[UserService, Depends(get_user_service)],
        user: Annotated[UserModel, Depends(get_user_or_404)],
    ):
        """
        Удаляет пользователя по заданному идентификатору.

        :param request: HTTP-запрос.
        :param user: Пользователь, найденный по ID.
        :param user_service: Сервис для работы с пользователями.
        """
        await user_service.delete(user, request=request)
        return None

    return router
