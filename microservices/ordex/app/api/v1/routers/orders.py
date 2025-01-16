from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from api.v1.common import (
    ErrorModel,
    ErrorCode,
    unauthorized_response,
    forbidden_response,
)
from api.v1.dependencies import Authenticator, get_order_service

from domain.schemas import (
    Order as OrderSchema,
    OrderCreate,
    OrderUpdate,
    User as UserSchema,
    OrderFilter,
)
from domain.exceptions import RecordNotFoundException, OrderIsConfirmedException
from domain.types import OpenAPIResponseType
from services import OrderService


def get_orders_router(
    prefix: str,
    tags: list[str],
    authenticator: Authenticator,
) -> APIRouter:
    """
    Создаёт и настраивает маршрутизатор для работы с заказами.

    :param prefix: Префикс URL для всех маршрутов этого роутера (например, "/orders").
    :param tags: Теги для классификации маршрутов в OpenAPI документации (например, ["Orders"]).
    :param authenticator: Объект аутентификации, предоставляющий зависимости для проверки пользователей.
    :return: Настроенный маршрутизатор с маршрутами для операций с заказами (получение, создание, обновление, удаление).

    Маршруты:
    - GET /{order_id}: Получение информации о заказе по ID.
    - GET /: Получение списка заказов с фильтрацией.
    - POST /: Создание нового заказа.
    - PUT /{order_id}: Обновление информации о заказе.
    - DELETE /{order_id}: Логическое удаление заказа (доступно только администраторам).

    Дополнительные зависимости и ответы:
    - `Depends(get_current_jwt_user)` проверяет авторизацию и верификацию пользователя.
    - `Depends(get_current_jwt_admin_user)` ограничивает доступ только администраторам для определённых маршрутов.
    - Обработаны ошибки 400 (например, когда заказ подтверждён и не может быть обновлён) и 404 (заказ не найден).
    """

    router = APIRouter(prefix=prefix, tags=tags)

    update_bad_response: OpenAPIResponseType = {
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.ORDER_IS_CONFIRMED: {
                            "summary": "Заказ со статусом 'CONFIRMED' не может быть изменён.",
                            "value": {"detail": ErrorCode.ORDER_IS_CONFIRMED},
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
                            "summary": "Order does not exist or is deleted",
                            "value": {"detail": ErrorCode.RECORD_NOT_FOUND},
                        }
                    }
                }
            },
        },
    }

    get_current_jwt_user = authenticator.current_jwt_user(
        is_active=True, is_verified=True
    )

    get_current_jwt_admin_user = authenticator.current_jwt_user(
        is_active=True, is_verified=True, required_roles=["admin"]
    )

    async def get_order_or_404(
        order_service: Annotated[OrderService, Depends(get_order_service)],
        order_id: int,
    ) -> OrderSchema:
        """
        Возвращает заказ по ID или вызывает HTTP 404, если заказ не найден.

        :param order_service: Сервис для работы с заказами.
        :param order_id: ID заказа.
        :return: Схема заказа.
        :raises HTTPException: Если заказ не найден.
        """
        try:
            return await order_service.get_by_id(order_id)
        except RecordNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    @router.get(
        "/{order_id}",
        response_model=OrderSchema,
        status_code=status.HTTP_200_OK,
        responses={
            **unauthorized_response,
            **not_found_response,
        },
        dependencies=[Depends(get_current_jwt_user)],
        name="orders:get_order",
    )
    async def get_order(
        order: Annotated[OrderSchema, Depends(get_order_or_404)],
    ):
        """
        Получает информацию о заказе по ID.

        :param order: Схема заказа, полученная через зависимость.
        :return: Схема заказа.
        """
        return order

    @router.get(
        "",
        response_model=list[OrderSchema],
        status_code=status.HTTP_200_OK,
        responses={
            **unauthorized_response,
            **forbidden_response,
            **not_found_response,
        },
        name="orders:get_filtered_orders",
    )
    async def get_filtered_orders(
        order_service: Annotated[OrderService, Depends(get_order_service)],
        user_token: Annotated[tuple[UserSchema, str], Depends(get_current_jwt_user)],
        order_filter: Annotated[OrderFilter, Query()],
    ):
        """
        Получает список заказов пользователя с возможностью фильтрации.

        :param order_service: Сервис для работы с заказами.
        :param user_token: Кортеж с данными пользователя и токеном.
        :param order_filter: Фильтры для поиска заказов.
        :return: Список схем заказов.
        """
        user, _ = user_token
        return await order_service.get_filtered(user.id, order_filter)

    @router.post(
        "",
        response_model=OrderSchema,
        status_code=status.HTTP_201_CREATED,
        responses=unauthorized_response,
        name="orders:create_order",
    )
    async def create_order(
        order_service: Annotated[OrderService, Depends(get_order_service)],
        user_token: Annotated[tuple[UserSchema, str], Depends(get_current_jwt_user)],
        order_create: OrderCreate,
    ):
        """
        Создаёт новый заказ.

        :param order_service: Сервис для работы с заказами.
        :param user_token: Кортеж с данными пользователя и токеном.
        :param order_create: Данные для создания заказа.
        :return: Схема созданного заказа.
        """
        user, _ = user_token
        created_order = await order_service.create(user.id, order_create)
        return created_order

    @router.put(
        "/{order_id}",
        response_model=OrderSchema,
        status_code=status.HTTP_200_OK,
        responses={
            **update_bad_response,
            **unauthorized_response,
            **not_found_response,
        },
        dependencies=[Depends(get_current_jwt_user)],
        name="orders:update_order",
    )
    async def update_order(
        order_service: Annotated[OrderService, Depends(get_order_service)],
        order_id: int,
        order_update: OrderUpdate,
    ):
        """
        Обновляет информацию о заказе.

        :param order_service: Сервис для работы с заказами.
        :param order_id: ID заказа для обновления.
        :param order_update: Данные для обновления заказа.
        :return: Схема обновлённого заказа.
        :raises HTTPException: Если заказ подтверждён или не найден.
        """
        try:
            return await order_service.update(order_id, order_update)
        except OrderIsConfirmedException:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.ORDER_IS_CONFIRMED,
            )
        except RecordNotFoundException:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.RECORD_NOT_FOUND,
            )

    @router.delete(
        "/{order_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            **unauthorized_response,
            **forbidden_response,
        },
        dependencies=[Depends(get_current_jwt_admin_user)],
        name="orders:soft_delete_order",
    )
    async def soft_delete_order(
        order_service: Annotated[OrderService, Depends(get_order_service)],
        order_id: int,
    ):
        """
        Логически удаляет заказ (доступно только администраторам).

        :param order_service: Сервис для работы с заказами.
        :param order_id: ID заказа для удаления.
        """
        await order_service.soft_delete(order_id)
        return None

    return router
