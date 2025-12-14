import uuid
import pytest

from http import HTTPStatus

from src.models import Course, Lesson


class TestTestQuestion:

    @pytest.mark.asyncio
    async def test_create_test_questions(
        self, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/test_questions/create: создание тестового вопроса"""
        token = access_token_admin
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()

        name = "Первый урок"
        payload = {
            "name": name,
            "desc": "Описание урока",
            "content": "Контент урока",
            "video_url": "http://example.com/jrn3o",
            "course_id": str(course.uuid),
        }
        lesson = Lesson(**payload)
        async_session.add(lesson)
        await async_session.commit()
        await async_session.refresh(lesson)

        req_url = f"/api/v1/test_questions/create"
        payload = {
              "question_num": 1,
              "desc": "Описание вопроса",
              "question": "Вопрос?",
              "choices": [
                "Ответ 1", "Ответ 2", "Ответ 3"
              ],
              "lesson_id": str(lesson.uuid),
              "correct_answer": "Ответ 1"
        }
        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        print(response)
        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()