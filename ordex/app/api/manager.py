from fastapi import APIRouter

from .v1 import Handler as V1Handler

from core.authentication.transports import bearer_transport
from core.authentication.strategies import jwt_strategy
from core.config import settings

BEARER_JWT_BACKEND_NAME = "bearer_jwt"


class ApiManager:
    """
    Управляет включением всех версий API в общий маршрутизатор.

    :return: Маршрутизатор с включёнными версиями API.

    Методы:
    - `get_router`: Возвращает маршрутизатор с подключёнными версиями API.
    """

    def __init__(self):
        self._router = APIRouter(prefix=settings.API.PREFIX)

        self._include_v1_router()

    def _include_v1_router(self) -> None:
        """
        Включает маршрутизатор версии API v1 в общий маршрутизатор.

        :return: None
        """
        v1_handler = V1Handler(
            name=BEARER_JWT_BACKEND_NAME,
            transport=bearer_transport,
            strategy=jwt_strategy,
        )

        self._router.include_router(v1_handler.get_router())

    def get_router(self) -> APIRouter:
        """
        Возвращает общий маршрутизатор API.

        :return: Маршрутизатор FastAPI.
        """
        return self._router
