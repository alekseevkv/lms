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

@pytest.fixture
def admin_payload() -> Dict[str, str]:
    return {"email": "admin@example.com", "password": "stringQwerty1!"}

@pytest_asyncio.fixture
async def access_token_admin(aiohttp_client, admin_payload: Dict[str, str]) -> Dict[str, str]:
    """Получение токена админа"""

    req_url = "/api/v1/auth/signup-admin"
    await aiohttp_client.post(req_url, json=admin_payload)

    req_url = "/api/v1/auth/signin"
    response = await aiohttp_client.post(req_url, json=admin_payload)
    content = await response.json()

    return content

@pytest_asyncio.fixture
async def create_lesson(aiohttp_client, access_token_admin: Dict[str, str]) -> Dict[str, str]:
    token = access_token_admin

    req_url = f"/api/v1/admin/course"
    payload = {"name": "Наименование курса", "desc": "Описание курса"}
    response = await aiohttp_client.post(
        req_url,
        json=payload,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    course = await response.json()

    req_url = f"/api/v1/lessons/create/"
    payload = {
        "name": "Первый урок",
        "desc": "Описание урока",
        "content": "Контент урока",
        "video_url": "http://example.com/jrn3o",
        "course_id": course["uuid"],
    }

    response = await aiohttp_client.post(
        req_url,
        json=payload,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    lesson = await response.json()
    return lesson

@pytest_asyncio.fixture
async def create_question(
    aiohttp_client, access_token_admin: Dict[str, str], create_lesson: Dict[str, str]
) -> Dict[str, str]:
    token = access_token_admin
    lesson = create_lesson

    req_url = "/api/v1/test_questions/create"
    payload = {
        "question_num": 1,
        "desc": "Описание вопроса",
        "question": "Вопрос?",
        "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
        "lesson_id": lesson["uuid"],
        "correct_answer": "Ответ 1",
    }
    response = await aiohttp_client.post(
        req_url,
        json=payload,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    question = await response.json()

    return question