from fastapi import APIRouter

from .v1 import Handler as V1Handler

from core.config import settings


class ApiManager:
    def __init__(self):
        self._router = APIRouter(prefix=settings.API.PREFIX)

        self._include_v1_router()

    def _include_v1_router(self) -> None:
        v1_handler = V1Handler()

        self._router.include_router(v1_handler.get_router())

    def get_router(self) -> APIRouter:
        return self._router
