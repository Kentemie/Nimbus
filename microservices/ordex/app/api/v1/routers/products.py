from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.common import ErrorModel, ErrorCode
from api.v1.dependencies import get_product_service

from domain.exceptions import RecordNotFoundException
from domain.schemas import Product as ProductSchema, ProductCreate, ProductUpdate
from domain.models import Product as ProductModel
from domain.types import OpenAPIResponseType
from services.product import ProductService


def get_products_router(prefix: str, tags: list[str]) -> APIRouter:
    """
    Создаёт маршрутизатор для управления продуктами.

    :param prefix: Префикс URL для маршрутов продуктов.
    :param tags: Теги для классификации маршрутов в документации OpenAPI.
    :return: Настроенный маршрутизатор с CRUD-эндпоинтами для продуктов.
    """

    router = APIRouter(prefix=prefix, tags=tags)

    not_found_response: OpenAPIResponseType = {
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.RECORD_NOT_FOUND: {
                            "summary": "Искомого продукта не существует.",
                            "value": {"detail": ErrorCode.RECORD_NOT_FOUND},
                        },
                    }
                }
            },
        }
    }

    async def get_product_or_404(
        product_service: Annotated[ProductService, Depends(get_product_service)],
        product_id: int,
    ) -> ProductModel:
        """
        Пытается получить продукт по ID, либо вызывает 404 ошибку.

        :param product_service: Сервис для работы с продуктами.
        :param product_id: Идентификатор продукта.
        :return: Объект модели продукта.
        :raises HTTPException: Если продукт не найден.
        """
        try:
            return await product_service.get_by_id(product_id)
        except RecordNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    @router.get(
        "/{product_id}",
        response_model=ProductSchema,
        status_code=status.HTTP_200_OK,
        responses=not_found_response,
        summary="Получить продукт по ID",
        name="products:get_product",
    )
    async def get_product(
        product: Annotated[ProductModel, Depends(get_product_or_404)],
    ):
        """
        Возвращает продукт по заданному идентификатору.

        :param product: Продукт, найденный с помощью зависимости get_product_or_404.
        :return: Данные продукта.
        """
        return ProductSchema.model_validate(product)

    @router.post(
        "",
        response_model=ProductSchema,
        status_code=status.HTTP_201_CREATED,
        summary="Создать новый продукт",
        name="products:create_product",
    )
    async def create_product(
        product_service: Annotated[ProductService, Depends(get_product_service)],
        product_create: ProductCreate,
    ):
        """
        Создаёт новый продукт.

        :param product_service: Сервис для работы с продуктами.
        :param product_create: Данные для создания продукта.
        :return: Созданный продукт.
        """
        created_product = await product_service.create(product_create)
        return ProductSchema.model_validate(created_product)

    @router.put(
        "/{product_id}",
        response_model=ProductSchema,
        status_code=status.HTTP_200_OK,
        responses=not_found_response,
        summary="Обновить продукт по ID",
        name="products:update_product",
    )
    async def update_product(
        product_service: Annotated[ProductService, Depends(get_product_service)],
        product: Annotated[ProductModel, Depends(get_product_or_404)],
        product_update: ProductUpdate,
    ):
        """
        Обновляет существующий продукт по заданному идентификатору.

        :param product_service: Сервис для работы с продуктами.
        :param product: Текущий продукт, найденный с помощью зависимости get_product_or_404.
        :param product_update: Данные для обновления продукта.
        :return: Обновлённый продукт.
        """
        updated_product = await product_service.update(product_update, product)
        return ProductSchema.model_validate(updated_product)

    @router.delete(
        "/{product_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        responses=not_found_response,
        summary="Удалить продукт по ID",
        name="products:delete_product",
    )
    async def delete_product(
        product_service: Annotated[ProductService, Depends(get_product_service)],
        product: Annotated[ProductModel, Depends(get_product_or_404)],
    ):
        """
        Удаляет продукт по заданному идентификатору.

        :param product_service: Сервис для работы с продуктами.
        :param product: Продукт, найденный с помощью зависимости get_product_or_404.
        """

        await product_service.delete(product)
        return None

    return router
