import uvicorn

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import api_manager

from core.config import settings
from core.infrastructure import postgres_manager, redis_manager, kafka_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    # startup
    await kafka_manager.start()
    yield
    # shutdown
    await postgres_manager.dispose()
    await redis_manager.close()
    await kafka_manager.stop()


app = FastAPI(
    debug=settings.APP.ENVIRONMENT == "staging",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(api_manager.get_router())

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP.HOST,
        port=settings.APP.PORT,
        reload=True,
    )
