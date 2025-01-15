from typing import Annotated, AsyncGenerator

from fastapi import Depends

from repositories.redis import OrderCacheRepository
from .repository import (
    get_user_repository,
    get_role_repository,
    get_order_db_repository,
    get_order_cache_repository,
    get_product_repository,
)

from repositories.postgres import *
from services import *
from domain.types import DependencyCallable


UserServiceDependency = DependencyCallable[UserService]


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    role_repository: Annotated[RoleRepository, Depends(get_role_repository)],
) -> AsyncGenerator[UserService, None]:
    yield UserService(user_repository, role_repository)


def get_role_service(
    role_repository: Annotated[RoleRepository, Depends(get_role_repository)]
) -> AsyncGenerator[RoleService, None]:
    yield RoleService(role_repository)


def get_order_service(
    order_db_repository: Annotated[OrderDBRepository, Depends(get_order_db_repository)],
    order_cache_repository: Annotated[
        OrderCacheRepository, Depends(get_order_cache_repository)
    ],
) -> AsyncGenerator[OrderService, None]:
    yield OrderService(order_db_repository, order_cache_repository)


def get_product_service(
    product_repository: Annotated[ProductRepository, Depends(get_product_repository)]
) -> AsyncGenerator[ProductService, None]:
    yield ProductService(product_repository)
