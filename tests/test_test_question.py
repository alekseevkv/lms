import uuid
from http import HTTPStatus

import pytest
from mypy.nodes import node_kinds

from src.models import Course, Lesson


class TestTestQuestion:
    @pytest.mark.asyncio
    async def test_create_test_questions(
        self, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/test_questions/create: создание тестового вопроса"""
        token = access_token_admin
        course = Course(name="Наименование курса", desc="Описание курса")
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

        req_url = "/api/v1/test_questions/create"
        payload = {
            "question_num": 1,
            "desc": "Описание вопроса",
            "question": "Вопрос?",
            "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
            "lesson_id": str(lesson.uuid),
            "correct_answer": "Ответ 1",
        }
        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.CREATED

        if response.status == HTTPStatus.CREATED:
            content = await response.json()
            assert content["question_num"] == 1


    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            (
                {
                    "payload": {
                        "desc": "Описание вопроса",
                        "question": "Вопрос?",
                        "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                        "lesson_id": str(uuid.uuid4()),
                        "correct_answer": "Ответ 1",
                    }
                },
                {"status": HTTPStatus.UNPROCESSABLE_CONTENT, "msg": "Field required"},
            ),
            (
                {
                    "payload": {
                        "question_num": 0,
                        "desc": "Описание вопроса",
                        "question": "Вопрос?",
                        "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                        "lesson_id": str(uuid.uuid4()),
                        "correct_answer": "Ответ 5",
                    }
                },
                {"status": HTTPStatus.UNPROCESSABLE_CONTENT, "msg": "Input should be greater than 0"},
            ),
            (
                {
                    "payload": {
                        "question_num": 1,
                        "desc": "Описание вопроса",
                        "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                        "lesson_id": str(uuid.uuid4()),
                        "correct_answer": "Ответ 1",
                    }
                },
                {"status": HTTPStatus.UNPROCESSABLE_CONTENT, "msg": "Field required"},
            ),
            (
                {
                    "payload": {
                        "question_num": 1,
                        "desc": "Описание вопроса",
                        "question": "Вопрос?",
                        "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                        "correct_answer": "Ответ 1",
                    }
                },
                {"status": HTTPStatus.UNPROCESSABLE_CONTENT, "msg": "Field required"},
            ),
            (
                {
                    "payload": {
                        "question_num": 1,
                        "desc": "Описание вопроса",
                        "question": "Вопрос?",
                        "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                        "lesson_id": str(uuid.uuid4()),
                    }
                },
                {"status": HTTPStatus.UNPROCESSABLE_CONTENT, "msg": "Field required"},
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_test_questions_error(
        self, query_data, expected_data, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/test_questions/create: неверные данные"""
        token = access_token_admin
        req_url = "/api/v1/test_questions/create"

        response = await aiohttp_client.post(
            req_url,
            json=query_data["payload"],
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == expected_data["status"]

        if response.status == expected_data["status"]:
            content = await response.json()
            assert content["detail"][0]["msg"] == expected_data["msg"]

    @pytest.mark.asyncio
    async def test_create_multiple_test_questions(
        self, aiohttp_client, async_session, access_token_admin, create_lesson
    ):
        """Тест /api/v1/test_questions/create_multiple: добавление нескольких тестов"""
        lesson = create_lesson
        token = access_token_admin

        req_url = "/api/v1/test_questions/create_multiple"
        payload = [
            {
                "question_num": 1,
                "desc": "Описание вопроса",
                "question": "Вопрос?",
                "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                "lesson_id": lesson["uuid"],
                "correct_answer": "Ответ 1",
            },
            {
                "question_num": 2,
                "desc": "Описание вопроса",
                "question": "Вопрос?",
                "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                "lesson_id": lesson["uuid"],
                "correct_answer": "Ответ 1",
            },
        ]
        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        assert response.status == HTTPStatus.CREATED

        if response.status == HTTPStatus.CREATED:
            content = await response.json()
            assert len(content) == len(payload)

        await async_session.commit()

    @pytest.mark.asyncio
    async def test_create_multiple_test_questions_error(
        self, aiohttp_client, async_session, access_token_admin, create_lesson
    ):
        """/api/v1/test_questions/create_multiple"""
        lesson = create_lesson
        token = access_token_admin

        req_url = "/api/v1/test_questions/create_multiple"
        payload = [
            {
                "question_num": 1,
                "desc": "Описание вопроса",
                "question": "Вопрос?",
                "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                "lesson_id": lesson["uuid"],
                "correct_answer": "Ответ 1",
            },
            {
                "desc": "Описание вопроса",
                "question": "Вопрос?",
                "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                "lesson_id": lesson["uuid"],
                "correct_answer": "Ответ 1",
            },
        ]
        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        assert response.status == HTTPStatus.UNPROCESSABLE_CONTENT

        if response.status == HTTPStatus.UNPROCESSABLE_CONTENT:
            content = await response.json()
            assert content["detail"][0]["msg"] == "Field required"

        await async_session.commit()

    @pytest.mark.asyncio
    async def test_get_all_test_questions(
        self, aiohttp_client, async_session, access_token_admin, create_lesson
    ):
        """Тест /api/v1/test_questions/: просмотр всех тестовых вопросов"""
        token = access_token_admin

        for i in  range(2):
            lesson = create_lesson

            req_url = "/api/v1/test_questions/create_multiple"
            payload = [
                {
                    "question_num": 1,
                    "desc": f"Описание вопроса {i}",
                    "question": "Вопрос?",
                    "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                    "lesson_id": lesson["uuid"],
                    "correct_answer": "Ответ 1",
                },
                {
                    "question_num": 2,
                    "desc": f"Описание вопроса{i}",
                    "question": "Вопрос?",
                    "choices": ["Ответ 1", "Ответ 2", "Ответ 3"],
                    "lesson_id": lesson["uuid"],
                    "correct_answer": "Ответ 1",
                },
            ]
            await aiohttp_client.post(
                req_url,
                json=payload,
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )

        req_url = "/api/v1/test_questions/"

        response = await aiohttp_client.get(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert len(content) == 4

        await async_session.commit()


    @pytest.mark.asyncio
    async def test_get_all_test_questions_null(
        self, aiohttp_client, access_token_admin,
    ):
        """Тест /api/v1/test_questions/: просмотр всех тестовых вопросов, вопросов нет"""
        token = access_token_admin

        req_url = "/api/v1/test_questions/"

        response = await aiohttp_client.get(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Test questions not found"

    @pytest.mark.asyncio
    async def test_get_test_questions(
        self, aiohttp_client, async_session, access_token, access_token_admin, create_lesson
    ):
        """Тест /api/v1/test_questions/{test_question_id}: просмотр тестового вопроса"""
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
        res = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        question = await res.json()

        token = access_token
        req_url = f"/api/v1/test_questions/{question["uuid"]}"
        response = await aiohttp_client.get(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()

            assert content["lesson_id"] == lesson["uuid"]

    @pytest.mark.asyncio
    async def test_get_test_questions_error(
        self, aiohttp_client, async_session, access_token
    ):
        """Тест /api/v1/test_questions/{test_question_id}: просмотр тестового несуществующего вопроса"""
        token = access_token
        req_url = f"/api/v1/test_questions/{uuid.uuid4()}"
        response = await aiohttp_client.get(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Test question not found"

    @pytest.mark.asyncio
    async def test_get_test_questions_by_lesson(
        self, aiohttp_client, async_session, access_token, access_token_admin, create_lesson,
    ):
        """Тест /api/v1/test_questions/lesson/{lesson_id}: просмотр вопросов у урока"""
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
        res = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        question = await res.json()
        print(question)
        print(lesson["uuid"])

        token = access_token
        req_url = f"/api/v1/test_questions/{lesson["uuid"]}/"

        response = await aiohttp_client.get(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()

            assert content["lesson_id"] == lesson["uuid"]

    @pytest.mark.asyncio
    async def test_get_test_questions_by_lesson_error(
        self, aiohttp_client, async_session, access_token,
    ):
        """Тест /api/v1/test_questions/lesson/{lesson_id}: просмотр вопросов у несуществующего урока"""
        token = access_token

        req_url = f"/api/v1/test_questions/{uuid.uuid4()}/"

        response = await aiohttp_client.get(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()

            assert content["detail"] == "Test question not found"


    @pytest.mark.asyncio
    async def test_update_test_questions(
        self, aiohttp_client, async_session, access_token_admin, create_lesson
    ):
        """Тест //api/v1/test_questions/update/{test_question_id}: изменение тестового вопроса"""
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

        req_url = f"/api/v1/test_questions/update/{question["uuid"]}"
        payload_new = {
            "question_num": 2,
        }
        response = await aiohttp_client.patch(
            req_url,
            json=payload_new,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["question_num"] == 2


    @pytest.mark.asyncio
    async def test_update_test_questions_error(
        self, aiohttp_client, async_session, access_token_admin, create_lesson
    ):
        """Тест /api/v1/test_questions/update/{test_question_id}: изменение несуществующего тестового вопроса"""
        token = access_token_admin

        req_url = f"/api/v1/test_questions/update/{uuid.uuid4()}/"
        payload_new = {
            "question_num": 2,
        }
        response = await aiohttp_client.patch(
            req_url,
            json=payload_new,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Test question not found"

    @pytest.mark.asyncio
    async def test_delete_test_questions(
        self, aiohttp_client, async_session, access_token_admin, create_lesson
    ):
        """Тест /api/v1/test_questions/delete/{test_question_id}: удаление тестового вопроса"""
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

        req_url = f"/api/v1/test_questions/delete/{question['uuid']}"
        response = await aiohttp_client.patch(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["message"] == "Test question deleted successfully"

    @pytest.mark.asyncio
    async def test_delete_test_questions_error(
        self, aiohttp_client, async_session, access_token_admin, create_lesson
    ):
        """Тест /api/v1/test_questions/delete/{test_question_id}: удаление несуществующего тестового вопроса"""
        token = access_token_admin

        req_url = f"/api/v1/test_questions/delete/{uuid.uuid4()}"
        response = await aiohttp_client.patch(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.BAD_REQUEST

        if response.status == HTTPStatus.BAD_REQUEST:
            content = await response.json()
            assert content["detail"] == "Test question not found"

    @pytest.mark.asyncio
    async def test_check_test_questions_error(
        self, aiohttp_client, async_session, access_token
    ):
        """Тест /api/v1/test_questions/check: проверка несуществующего тестового вопроса"""
        token = access_token

        req_url = f"/api/v1/test_questions/check"

        payload = {
            "user_answers": [{"uuid": str(uuid.uuid4()), "user_answer": "ответ 1"}]
        }

        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.BAD_REQUEST

        if response.status == HTTPStatus.BAD_REQUEST:
            content = await response.json()
            assert content["detail"] == "Test question not found"

    @pytest.mark.asyncio
    async def test_check_test_questions(
        self, aiohttp_client, async_session, access_token, create_question
    ):
        """Тест /api/v1/test_questions/check: проверка верного тестового вопроса"""
        token = access_token
        question = create_question

        req_url = f"/api/v1/test_questions/check"

        payload ={
            "user_answers": [
                {
                    "uuid": question["uuid"],
                    "user_answer": "ответ 1"
                }
            ]
        }

        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["checked_answers"][0]["passed"] == True


    @pytest.mark.asyncio
    async def test_check_test_questions_mistake(
        self, aiohttp_client, async_session, access_token, create_question
    ):
        """Тест /api/v1/test_questions/check: проверка неверного тестового вопроса"""
        token = access_token
        question = create_question

        req_url = f"/api/v1/test_questions/check"

        payload ={
            "user_answers": [
                {
                    "uuid": question["uuid"],
                    "user_answer": "ответ 3"
                }
            ]
        }

        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["checked_answers"][0]["passed"] == False

    @pytest.mark.asyncio
    async def test_estimate_test_questions(
        self, aiohttp_client, async_session, access_token, create_question
    ):
        """Тест /api/v1/test_questions/estimate/{lesson_id}: оценка к верному уроку"""
        token = access_token
        question = create_question

        req_url = f"/api/v1/test_questions/estimate/{question['lesson_id']}"

        payload = {
            "user_answers": [{"uuid": question["uuid"], "user_answer": "ответ 1"}]
        }

        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["percentage"] == 100.0

    @pytest.mark.asyncio
    async def test_estimate_test_questions_zero(
        self, aiohttp_client, async_session, access_token, create_question
    ):
        """Тест /api/v1/test_questions/estimate/{lesson_id}: оценка к неверному уроку"""
        token = access_token
        question = create_question

        req_url = f"/api/v1/test_questions/estimate/{question["lesson_id"]}"

        payload = {
            "user_answers": [{"uuid": question["uuid"], "user_answer": "ответ 3"}]
        }

        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["percentage"] == 0.0


    @pytest.mark.asyncio
    async def test_estimate_test_questions_error(
        self, aiohttp_client, async_session, access_token, create_question
    ):
        """Тест /api/v1/test_questions/estimate/{lesson_id}: оценка к несуществующему уроку"""
        token = access_token

        req_url = f"/api/v1/test_questions/estimate/{uuid.uuid4()}"

        payload ={
            "user_answers": [
                {
                    "uuid": str(uuid.uuid4()),
                    "user_answer": "ответ 3"
                }
            ]
        }

        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            print(content)
