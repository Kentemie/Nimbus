from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.common import ErrorModel, ErrorCode
from api.v1.dependencies import get_role_service

from domain.exceptions import RecordNotFoundException
from domain.schemas import Role as RoleSchema, RoleCreate, RoleUpdate
from domain.models import Role as RoleModel
from services.role import RoleService
from domain.types import OpenAPIResponseType


def get_roles_router(prefix: str, tags: list[str]) -> APIRouter:
    """
    Создаёт маршрутизатор для управления ролями.

    :param prefix: Префикс URL для маршрутов ролей.
    :param tags: Теги для классификации маршрутов в документации OpenAPI.
    :return: Настроенный маршрутизатор с CRUD-эндпоинтами для ролей.
    """

    router = APIRouter(prefix=prefix, tags=tags)

    not_found_response: OpenAPIResponseType = {
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.RECORD_NOT_FOUND: {
                            "summary": "Искомой роли не существует.",
                            "value": {"detail": ErrorCode.RECORD_NOT_FOUND},
                        },
                    }
                }
            },
        }
    }

    async def get_role_or_404(
        role_service: Annotated["RoleService", Depends(get_role_service)],
        role_id: int,
    ) -> "RoleModel":
        """
        Пытается получить продукт по ID, либо вызывает 404 ошибку.

        :param role_service: Сервис для работы с ролями.
        :param role_id: Идентификатор роли.
        :return: Объект модели роли.
        :raises HTTPException: Если роль не найдена.
        """
        try:
            return await role_service.get_by_id(role_id)
        except RecordNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    @router.get(
        "/{role_id}",
        response_model=RoleSchema,
        status_code=status.HTTP_200_OK,
        responses={
            **not_found_response,
        },
        summary="Получить роль по ID",
        name="roles:get_role",
    )
    async def get_role(
        role: Annotated[RoleModel, Depends(get_role_or_404)],
    ):
        """
        Возвращает роль по заданному идентификатору.

        :param role: Роль, полученная с помощью зависимости get_role_or_404.
        :return: Данные роли.
        """
        return RoleSchema.model_validate(role)

    @router.post(
        "",
        response_model=RoleSchema,
        status_code=status.HTTP_201_CREATED,
        summary="Создать новую роль",
        name="roles:create_role",
    )
    async def create_role(
        role_service: Annotated["RoleService", Depends(get_role_service)],
        role_create: RoleCreate,
    ):
        """
        Создаёт новую роль.

        :param role_service: Сервис для управления ролями.
        :param role_create: Данные для создания новой роли.
        :return: Созданная роль.
        """
        created_role = await role_service.create(role_create)
        return RoleSchema.model_validate(created_role)

    @router.put(
        "/{role_id}",
        response_model=RoleSchema,
        status_code=status.HTTP_200_OK,
        summary="Обновить роль по ID",
        name="roles:update_role",
    )
    async def update_role(
        role_service: Annotated["RoleService", Depends(get_role_service)],
        role: Annotated["RoleModel", Depends(get_role_or_404)],
        role_update: RoleUpdate,
    ):
        """
        Обновляет существующую роль по заданному идентификатору.

        :param role_service: Сервис для управления ролями.
        :param role_update: Данные для обновления роли.
        :param role: Текущая роль, полученная с помощью зависимости get_role_or_404.
        :return: Обновлённая роль.
        """
        updated_role = await role_service.update(role_update, role)
        return RoleSchema.model_validate(updated_role)

    @router.delete(
        "/{role_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Удалить роль по ID",
        name="roles:delete_role",
    )
    async def delete_role(
        role_service: Annotated["RoleService", Depends(get_role_service)],
        role: Annotated["RoleModel", Depends(get_role_or_404)],
    ):
        """
        Удаляет роль по заданному идентификатору.

        :param role_service: Сервис для управления ролями.
        :param role: Роль, полученная с помощью зависимости get_role_or_404.
        """
        await role_service.delete(role)
        return None

    return router
