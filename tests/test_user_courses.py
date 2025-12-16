import uuid
from http.client import responses

import pytest

from http import HTTPStatus

from src.models.course import Course

class TestUserCourses:

    @pytest.mark.asyncio
    async def test_enroll_course(
        self, aiohttp_client, async_session, access_token
    ):
        """Тест /api/v1/user_courses/enroll/{course_id}: запись на курс"""
        token = access_token
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()

        req_url = f"/api/v1/user_courses/enroll/{course.uuid}"
        response = await aiohttp_client.post(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.CREATED

        if response.status == HTTPStatus.CREATED:
            content = await response.json()
            assert content["course_id"] == str(course.uuid)

    @pytest.mark.asyncio
    async def test_enroll_course_error(
        self, aiohttp_client, async_session, access_token
    ):
        """Тест /api/v1/user_courses/enroll/{course_id}: запись на несуществующий курс"""
        token = access_token

        req_url = f"/api/v1/user_courses/enroll/{uuid.uuid4()}"
        response = await aiohttp_client.post(
            req_url,
            headers={"Authorization": f"Bearer {token["access_token"]}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Course not found"

    #@pytest.mark.asyncio
    #async def test_start_lesson(self, aiohttp_client, async_session, access_token, create_lesson):
    #    """Тест /api/v1/user_courses/lessons/{lesson_id}/start: запись на урок (пользователь не записан на курс)"""
    #    token = access_token
    #    lesson = create_lesson

    #    req_url = f"/api/v1/user_courses/lessons/{lesson["uuid"]}/start"
    #    response = await aiohttp_client.post(
    #        req_url,
    #        headers={"Authorization": f"Bearer {token["access_token"]}"},
    #    )

    #    assert response.status == HTTPStatus.OK

    #    if response.status == HTTPStatus.OK:
    #        content = await response.json()
    #        assert content["lesson_id"] == lesson["uuid"]
    #        assert content["message"] == "Lesson started successfully. You can now proceed with the test."

    #    async_session.commit()


    #@pytest.mark.asyncio
    #async def test_start_new_lesson(self, aiohttp_client, async_session, access_token, create_lesson):
    #    """Тест /api/v1/user_courses/lessons/{lesson_id}/start: запись на урок (пользователь записан на курс)"""
    #    token = access_token
    #    lesson = create_lesson

    #    req_url = f" /api/v1/user_courses/enroll/{lesson["course_id"]}"
    #    await aiohttp_client.post(
    #        req_url,
    #        headers={"Authorization": f"Bearer {token["access_token"]}"},
    #    )

    #    req_url = f"/api/v1/user_courses/lessons/{lesson["uuid"]}/start"
    #    response = await aiohttp_client.post(
    #        req_url,
    #        headers={"Authorization": f"Bearer {token["access_token"]}"},
    #    )

    #    assert response.status == HTTPStatus.OK

    #    if response.status == HTTPStatus.OK:
    #        content = await response.json()
    #        assert content["lesson_id"] == lesson["uuid"]
    #        assert content["message"] == "Lesson started successfully. You can now proceed with the test."

    #    async_session.commit()


    @pytest.mark.asyncio
    async def test_start_lesson_error(
        self, aiohttp_client, async_session, access_token, create_lesson
    ):
        """Тест /api/v1/user_courses/lessons/{lesson_id}/start: запись на несуществующий урок"""
        token = access_token

        req_url = f"/api/v1/user_courses/lessons/{uuid.uuid4()}/start"
        response = await aiohttp_client.post(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Lesson not found"

        async_session.commit()


    @pytest.mark.asyncio
    async def test_get_lesson_progress(
        self, aiohttp_client, async_session, access_token, create_lesson
    ):
        """Тест /api/v1/user_courses/lessons/{lesson_id}/progress: прогресс по уроку (пользователь начал урок)"""
        token = access_token
        lesson = create_lesson

        req_url = f"/api/v1/user_courses/lessons/{lesson['uuid']}/start"
        response_lesson = await aiohttp_client.post(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        content = await response_lesson.json()
        print(content)
        req_url = f"/api/v1/user_courses/lessons/{lesson['uuid']}/progress"
        response = await aiohttp_client.get(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        content = await response.json()
        print(content)
        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["lesson_id"] == lesson["uuid"]

        async_session.commit()


    #@pytest.mark.asyncio
    #async def test_get_lesson_not_progress(
    #    self, aiohttp_client, async_session, access_token, create_lesson
    #):
    #    """Тест /api/v1/user_courses/lessons/{lesson_id}/progress: прогресс по уроку (пользователь не записан на урок)"""
    #    token = access_token
     #   lesson = create_lesson

    #    req_url = f"/api/v1/user_courses/lessons/{lesson['uuid']}/progress"
    #    response = await aiohttp_client.get(
    #        req_url,
    #        headers={"Authorization": f"Bearer {token['access_token']}"},
    #    )

    #    assert response.status == HTTPStatus.OK

    #    if response.status == HTTPStatus.OK:
    #        content = await response.json()
    #        assert content["lesson_id"] == lesson["uuid"]
    #        assert content["message"] == "Lesson not started yet"


    @pytest.mark.asyncio
    async def test_get_lesson_progress_error(
        self, aiohttp_client, async_session, access_token, create_lesson
    ):
        """Тест /api/v1/user_courses/lessons/{lesson_id}/progress: прогресс по несуществующему уроку"""
        token = access_token

        req_url = f"/api/v1/user_courses/lessons/{uuid.uuid4()}/progress"
        response = await aiohttp_client.get(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Lesson not found"