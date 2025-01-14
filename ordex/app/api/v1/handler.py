from fastapi import APIRouter

from .dependencies import Authenticator, get_user_service
from .routers import *

from core.authentication import AuthenticationBackend
from core.authentication.transports import bearer_transport
from core.authentication.strategies import jwt_strategy
from core.config import settings


class Handler:
    def __init__(self) -> None:
        self._router = APIRouter(prefix=settings.API.V1.PREFIX)
        self._auth_backend = AuthenticationBackend(
            name="BEARER_JWT",
            transport=bearer_transport,
            strategy=jwt_strategy,
        )

        self._authenticator = Authenticator(
            backend=self._auth_backend,
            get_user_service=get_user_service,
        )

        self._gather_routers()

    def _gather_routers(self) -> None:
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
        return self._router
