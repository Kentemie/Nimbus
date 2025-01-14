from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.infrastructure import postgres_manager
from repositories.postgres import *


def get_user_repository(
    session: Annotated[AsyncSession, Depends(postgres_manager.get_session)]
) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(session=session)


def get_role_repository(
    session: Annotated[AsyncSession, Depends(postgres_manager.get_session)]
) -> AsyncGenerator[RoleRepository, None]:
    yield RoleRepository(session=session)


def get_order_repository(
    session: Annotated[AsyncSession, Depends(postgres_manager.get_session)]
) -> AsyncGenerator[OrderRepository, None]:
    yield OrderRepository(session=session)


def get_product_repository(
    session: Annotated[AsyncSession, Depends(postgres_manager.get_session)]
) -> AsyncGenerator[ProductRepository, None]:
    yield ProductRepository(session=session)
