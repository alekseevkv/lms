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
    async def test_create_course_not_desc(self, aiohttp_client, async_session, access_token_admin):
        """Тест /api/v1/admin/course: создание курса без наименования"""
        token = access_token_admin

        req_url = f"/api/v1/admin/course"
        payload = {"name":"Наименование курса"}
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
        """Тест /api/v1/admin/course/{course_id}/update: неверный uuid курса"""
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


    @pytest.mark.asyncio
    async def test_course_delete(self, aiohttp_client, async_session, access_token_admin):
        """Тест /api/v1/admin/course/{course_id}/delete: удаление курса"""
        course = Course(name="Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()
        await async_session.refresh(course)

        token = access_token_admin

        req_url = f"/api/v1/admin/course/{course.uuid}/delete"
        response = await aiohttp_client.patch(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["message"] == "Course delete successfully"

    @pytest.mark.asyncio
    async def test_delete_course_error(
        self, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/admin/course/{course_id}/delete: неверный uuid курса"""
        course = Course(name="Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()
        await async_session.refresh(course)

        token = access_token_admin

        req_url = f"/api/v1/admin/course/{uuid.uuid4()}/delete"
        response = await aiohttp_client.patch(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.BAD_REQUEST

        if response.status == HTTPStatus.BAD_REQUEST:
            content = await response.json()
            assert content["detail"] == "Course not found"

    @pytest.mark.asyncio
    async def test_update_users(
        self, aiohttp_client, async_session, access_token_admin, user_payload
    ):
        """Тест /api/v1/admin/users: обновление данных о пользователе"""
        req_url = "/api/v1/auth/signup"
        await aiohttp_client.post(req_url, json=user_payload)

        token = access_token_admin

        req_url = f"/api/v1/admin/users"

        payload = {
            "email": user_payload["email"],
            "roles": [
                "student"
            ]
        }
        response = await aiohttp_client.patch(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["email"] == user_payload["email"]
            assert content["roles"] == payload["roles"]

    @pytest.mark.asyncio
    async def test_update_users_error(
        self, aiohttp_client, async_session, access_token_admin, user_payload
    ):
        """Тест /api/v1/admin/users: некорректный email пользователя"""
        req_url = "/api/v1/auth/signup"
        await aiohttp_client.post(req_url, json=user_payload)

        token = access_token_admin

        req_url = f"/api/v1/admin/users"

        payload = {
            "email": "test_user@email.com",
            "roles": [
                "student"
            ]
        }
        response = await aiohttp_client.patch(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.BAD_REQUEST

        if response.status == HTTPStatus.BAD_REQUEST:
            content = await response.json()
            content["detail"] = "There is no user with such credentials"

    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            (
                {"req_url": "/api/v1/admin/course",
                 "method": "post",
                },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
            (
                {"req_url": f"/api/v1/admin/course/4a6e5502-3cf6-4e4c-8490-051afb9771a7/update",
                 "method": "patch",
                 },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
            (
                {"req_url": f"/api/v1/admin/course/{uuid.uuid4()}/delete",
                 "method": "patch",
                 },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
            (
                {"req_url": "/api/v1/admin/users",
                 "method": "patch",
                 },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_not_authorization(self, query_data, expected_data, aiohttp_client, async_session):
        """Тесты без авторизации"""
        if query_data["method"] == "post":
            response = await aiohttp_client.post(query_data["req_url"], json={})
        elif query_data["method"] == "patch":
            response = await aiohttp_client.patch(
                query_data["req_url"], json=expected_data
            )

        assert response.status == expected_data["status"]

        if response.status == expected_data["status"]:
            content = await response.json()
            assert content["detail"] == expected_data["detail"]

        await async_session.commit()


    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            (
                {
                    "req_url": "/api/v1/admin/course",
                    "method": "post",
                    "payload": {"name": "Пример", "desc": "string"},
                },
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "detail": f"User can only be updated by admin",
                },
            ),
            (
                {
                    "req_url": f"/api/v1/admin/course/4a6e5502-3cf6-4e4c-8490-051afb9771a7/update",
                    "method": "patch",
                    "payload": {},
                },
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "detail": f"User can only be updated by admin",
                },
            ),
            (
                {
                    "req_url": f"/api/v1/admin/course/{uuid.uuid4()}/delete",
                    "method": "patch",
                    "payload": {},
                },
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "detail": f"User can only be updated by admin",
                },
            ),
            (
                {
                    "req_url": "/api/v1/admin/users",
                    "method": "patch",
                    "payload": {
                        "email": "user@example.com",
                        "new_email": "user@example.com"
                    },
                },
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "detail": f"User can only be updated by admin",
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_admin_user(self, query_data, expected_data, access_token, aiohttp_client, async_session):
        """Тесты от пользователей не админов"""
        token = access_token

        if query_data["method"] == "post":
            response = await aiohttp_client.post(
                query_data["req_url"],
                json=query_data["payload"],
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
        elif query_data["method"] == "patch":
            response = await aiohttp_client.patch(
                query_data["req_url"],
                json=query_data["payload"],
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )

        assert response.status == expected_data["status"]

        if response.status == expected_data["status"]:
            content = await response.json()
            assert content["detail"] == expected_data["detail"]

        await async_session.commit()
