from fastapi import FastAPI

from src.api.v1.auth_api import router as auth_router
from src.api.v1.course_api import router as course_router

from .configs.app import settings

app = FastAPI(
    title=settings.app.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(course_router, prefix="/api/v1/courses", tags=["course"])
