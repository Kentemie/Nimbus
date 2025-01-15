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
from domain.models import Order as OrderModel
from domain.exceptions import RecordNotFoundException, OrderIsConfirmedException
from domain.types import OpenAPIResponseType
from services import OrderService


def get_orders_router(
    prefix: str,
    tags: list[str],
    authenticator: Authenticator,
) -> APIRouter:
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
    ) -> OrderModel:
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
        order: Annotated[OrderModel, Depends(get_order_or_404)],
    ):
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
        Получить все «живые» (не удалённые) заказы пользователя.
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
        await order_service.soft_delete(order_id)
        return None

    return router
