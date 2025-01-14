from fastapi import APIRouter

from .v1 import Handler as ApiV1Handler

from core.config import settings


class ApiManager:
    def __init__(self):
        self._router = APIRouter(prefix=settings.API.PREFIX)

        self._include_v1_router()

    def _include_v1_router(self) -> None:
        api_v1_handler = ApiV1Handler()

        self._router.include_router(api_v1_handler.get_router())

    def get_router(self) -> APIRouter:
        return self._router
