from typing import Dict

import pytest
import pytest_asyncio
import aiohttp

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fastapi.testclient import TestClient
from src.main import app
from src.models.base import Base
from src.configs.app import settings


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def aiohttp_client():
    session = aiohttp.ClientSession(base_url="http://localhost:8000")
    yield session
    await session.close()


@pytest_asyncio.fixture(scope="function")
async def for_test_engine():
    engine = create_async_engine(settings.db.dsl_test)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

        await conn.commit()


@pytest_asyncio.fixture(scope="function")
async def async_session(for_test_engine):

    async_session_factory = sessionmaker(
        for_test_engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session_factory() as session:
        yield session


@pytest.fixture
def user_payload() -> Dict[str, str]:
    return {"email": "user@example.com", "password": "stringQwerty1!"}

@pytest_asyncio.fixture
async def access_token(aiohttp_client, user_payload: Dict[str, str]) -> Dict[str, str]:
    """Получение токена пользователя"""

    req_url = "/api/v1/auth/signup"
    await aiohttp_client.post(req_url, json=user_payload)

    req_url = "/api/v1/auth/signin"
    response = await aiohttp_client.post(req_url, json=user_payload)
    content = await response.json()

    return content