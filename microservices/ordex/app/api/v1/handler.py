from fastapi import APIRouter

from .dependencies import Authenticator, get_user_service
from .routers import *

from core.authentication import AuthenticationBackend
from core.authentication.transports import Transport
from core.authentication.strategies import Strategy
from core.config import settings


class Handler:
    """
    Управляет настройкой маршрутов для версии API v1.

    :param name: Название бэкенда аутентификации.
    :param transport: Транспорт для работы с токенами.
    :param strategy: Стратегия генерации и валидации токенов.

    Маршруты:
    - Аутентификация и регистрация: Login, Register, Verify, Reset Password.
    - Управление пользователями и ролями: Users, User Roles.
    - Работа с заказами и продуктами: Orders, Products.

    Методы:
    - `get_router`: Возвращает маршрутизатор для API v1.
    """

    def __init__(self, name: str, transport: Transport, strategy: Strategy) -> None:
        self._router = APIRouter(prefix=settings.API.V1.PREFIX)
        self._auth_backend = AuthenticationBackend(
            name=name,
            transport=transport,
            strategy=strategy,
        )

        self._authenticator = Authenticator(
            backend=self._auth_backend,
            get_user_service=get_user_service,
        )

        self._gather_routers()

    def _gather_routers(self) -> None:
        """
        Собирает и включает маршрутизаторы для различных функций API v1.

        :return: None
        """
        self._router.include_router(
            router=get_auth_router(
                prefix=settings.API.V1.AUTH,
                tags=["Auth"],
                authenticator=self._authenticator,
                backend=self._auth_backend,
                requires_verification=True,
            )
        )

        self._router.include_router(
            router=get_register_router(
                prefix=settings.API.V1.AUTH,
                tags=["Auth"],
            )
        )

        self._router.include_router(
            router=get_verify_router(
                prefix=settings.API.V1.AUTH,
                tags=["Auth"],
            )
        )

        self._router.include_router(
            router=get_reset_password_router(
                prefix=settings.API.V1.AUTH,
                tags=["Auth"],
            )
        )

        self._router.include_router(
            router=get_users_router(
                prefix=settings.API.V1.USERS,
                tags=["Users"],
                authenticator=self._authenticator,
                requires_verification=True,
            )
        )

        self._router.include_router(
            router=get_roles_router(
                prefix=settings.API.V1.ROLES,
                tags=["User roles"],
            )
        )

        self._router.include_router(
            router=get_orders_router(
                prefix=settings.API.V1.ORDERS,
                tags=["Orders"],
                authenticator=self._authenticator,
            )
        )

        self._router.include_router(
            router=get_products_router(
                prefix=settings.API.V1.PRODUCTS,
                tags=["Products"],
            )
        )

    def get_router(self) -> APIRouter:
        """
        Возвращает маршрутизатор с настроенными маршрутами API v1.

        :return: Маршрутизатор FastAPI.
        """
        return self._router
