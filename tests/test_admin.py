import uuid
from http import HTTPStatus

import pytest

from src.models import Course


class TestAdmin:

    @pytest.mark.asyncio
    async def test_create_course(self, aiohttp_client, async_session, access_token_admin):
        """Тест /api/v1/admin/course: создание курса"""
        token = access_token_admin

        req_url = f"/api/v1/admin/course"
        name_course = "Наименование курса"
        payload = {"name":name_course, "desc":"Описание курса"}
        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["name"] == name_course


    @pytest.mark.asyncio
    async def test_create_course_error(self, aiohttp_client, async_session, access_token_admin):
        """Тест /api/v1/admin/course: создание курса без наименования"""
        token = access_token_admin

        req_url = f"/api/v1/admin/course"
        payload = {"desc":"Описание курса"}
        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.UNPROCESSABLE_CONTENT

        if response.status == HTTPStatus.UNPROCESSABLE_CONTENT:
            content = await response.json()
            assert content["detail"][0]["msg"] == "Field required"

    @pytest.mark.asyncio
    async def test_create_course_double(self, aiohttp_client, async_session, access_token_admin):
        """Тест /api/v1/admin/course: создание уже существующего курса"""
        course = Course(name="Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()

        token = access_token_admin

        req_url = f"/api/v1/admin/course"
        name_course = "Наименование курса"
        payload = {"name":name_course, "desc":"Описание курса"}
        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.BAD_REQUEST

        if response.status == HTTPStatus.BAD_REQUEST:
            content = await response.json()
            assert content["detail"] == "A course with this name already exists"


    @pytest.mark.asyncio
    async def test_update_course(self, aiohttp_client, async_session, access_token_admin):
        """Тест /api/v1/admin/course/{course_id}/update: обновление курса"""
        course = Course(name="Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()
        await async_session.refresh(course)

        token = access_token_admin

        req_url = f"/api/v1/admin/course/{course.uuid}/update"
        name_course = "Новое наименование курса"
        payload = {"name":name_course, "desc": "Новое описание курса"}
        response = await aiohttp_client.patch(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["name"] == name_course

    @pytest.mark.asyncio
    async def test_update_course_not_name(self, aiohttp_client, async_session, access_token_admin):
        """Тест /api/v1/admin/course/{course_id}/update: не верный uuid курса"""
        course = Course(name="Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()
        await async_session.refresh(course)

        token = access_token_admin

        req_url = f"/api/v1/admin/course/{uuid.uuid4()}/update"
        payload = {"desc": "Новое описание курса"}
        response = await aiohttp_client.patch(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Course not found"


    @pytest.mark.asyncio
    async def test_update_course_double_name(
        self, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/admin/course/{course_id}/update: попытка изменить имя курса на уже существующее"""
        course = Course(name="Математика", desc=f"Описание курса")
        async_session.add(course)

        course_new = Course(name="Наименование курса", desc=f"Описание курса")
        async_session.add(course_new)

        await async_session.commit()
        await async_session.refresh(course)
        await async_session.refresh(course_new)

        token = access_token_admin

        req_url = f"/api/v1/admin/course/{course_new.uuid}/update"
        payload = {"name": "Математика"}
        response = await aiohttp_client.patch(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.BAD_REQUEST

        if response.status == HTTPStatus.BAD_REQUEST:
            content = await response.json()
            assert content["detail"] == "A course with this name already exists"

    @pytest.mark.asyncio
    async def test_update_course_name(self, aiohttp_client, async_session, access_token_admin):
        """Тест /api/v1/admin/course/{course_id}/update: пустое имя"""
        course = Course(name="Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()
        await async_session.refresh(course)

        token = access_token_admin

        req_url = f"/api/v1/admin/course/{course.uuid}/update"
        payload = {"name": ""}
        response = await aiohttp_client.patch(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        content = await response.json()
        print(f"Имя курса: {content['name']}")
