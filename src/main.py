from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from src.api.v1.auth_api import router as auth_router
from src.api.v1.course_api import router as course_router
from src.redis_client import set_redis_client

from .configs.app import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(
        host=settings.redis.redis_host,
        port=settings.redis.redis_port,
        db=settings.redis.redis_db,
        password=settings.redis.redis_password or None,
        decode_responses=True,
    )
    set_redis_client(redis)
    yield
    await redis.close()
    await redis.connection_pool.disconnect()


app = FastAPI(
    title=settings.app.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(course_router, prefix="/api/v1/courses", tags=["course"])
