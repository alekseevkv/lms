import uuid
import pytest

from http import HTTPStatus

from src.models import Course, Lesson


class TestLessons:

    @pytest.mark.asyncio
    async def test_create_lesson(
        self, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/lessons/create/: создание курса"""
        token = access_token_admin
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()

        req_url = f"/api/v1/lessons/create/"
        name = "Первый урок"
        payload = {
            "name": name,
            "desc": "Описание урока",
            "content": "Контент урока",
            "video_url": "http://example.com/jrn3o",
            "course_id": str(course.uuid),
        }

        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.CREATED

        if response.status == HTTPStatus.CREATED:
            content = await response.json()
            assert content["name"] == name

    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            (
                {
                    "payload": {
                        "desc": "Описание урока",
                        "content": "Контент урока",
                        "video_url": "http://example.com/jrn3o",
                        "course_id": str(uuid.uuid4()),
                    }
                },
                {"status": HTTPStatus.UNPROCESSABLE_CONTENT, "msg": "Field required"},
            ),
            (
                {
                    "payload": {
                        "name": "Первый урок",
                        "desc": "Описание урока",
                        "video_url": "http://example.com/jrn3o",
                        "course_id": str(uuid.uuid4()),
                    }
                },
                {"status": HTTPStatus.UNPROCESSABLE_CONTENT, "msg": "Field required"},
            ),
            (
                {
                    "payload": {
                        "name": "Первый урок",
                        "desc": "Описание урока",
                        "content": "Контент урока",
                        "video_url": "http://example.com/jrn3o",
                    }
                },
                {"status": HTTPStatus.UNPROCESSABLE_CONTENT, "msg": "Field required"},
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_lesson_error(
        self, query_data, expected_data, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/lessons/create/: без обязательных полей"""
        token = access_token_admin
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()

        req_url = f"/api/v1/lessons/create/"

        response = await aiohttp_client.post(
            req_url,
            json=query_data["payload"],
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == expected_data["status"]

        if response.status == HTTPStatus.UNPROCESSABLE_CONTENT:
            content = await response.json()
            assert content["detail"][0]["msg"] == expected_data["msg"]

    # @pytest.mark.asyncio
    # async def test_create_lesson_not_course(
    #     self, aiohttp_client, async_session, access_token_admin
    # ):
    #     """Тест /api/v1/lessons/create/: создание урока к несуществующему курсу"""
    #     token = access_token_admin
    #
    #     req_url = f"/api/v1/lessons/create/"
    #     name = "Первый урок"
    #     payload = {
    #         "name": name,
    #         "desc": "Описание урока",
    #         "content": "Контент урока",
    #         "video_url": "http://example.com/jrn3o",
    #         "course_id": str(uuid.uuid4()),
    #     }
    #
    #     response = await aiohttp_client.post(
    #         req_url,
    #         json=payload,
    #         headers={"Authorization": f"Bearer {token['access_token']}"},
    #     )
    #     content = await response.json()
    #     print(content)

        # здесь должно быть описание ошибки
        # assert response.status == HTTPStatus.OK
        #
        # if response.status == HTTPStatus.OK:
        #     content = await response.json()
        #     assert content["name"] == name

        await async_session.commit()

    @pytest.mark.asyncio
    async def test_create_lesson_double(
        self, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/lessons/create/: создание урока к несуществующему курсу"""
        token = access_token_admin
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()

        req_url = f"/api/v1/lessons/create/"
        name = "Первый урок"
        payload = {
            "name": name,
            "desc": "Описание урока",
            "content": "Контент урока",
            "video_url": "http://example.com/jrn3o",
            "course_id": str(course.uuid),
        }

        await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.BAD_REQUEST

        if response.status == HTTPStatus.BAD_REQUEST:
            content = await response.json()
            assert (
                content["detail"]
                == "A lesson with this name already exists in this course"
            )

    @pytest.mark.asyncio
    async def test_update_lesson(
        self, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/lessons/update/{lesson_id}: обновление урока"""
        token = access_token_admin

        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()
        await async_session.refresh(course)

        payload = {
            "name": "Первый урок",
            "desc": "Описание урока",
            "content": "Контент урока",
            "video_url": "http://example.com/jrn3o",
            "course_id": str(course.uuid),
        }
        lesson = Lesson(**payload)
        async_session.add(lesson)
        await async_session.commit()
        await async_session.refresh(lesson)

        req_url = f"/api/v1/lessons/update/{lesson.uuid}"

        new_name = "Второй урок"
        update_payload = {"name":new_name}
        response = await aiohttp_client.put(
            req_url,
            json=update_payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["name"] == new_name

    @pytest.mark.asyncio
    async def test_update_lesson_error(
        self, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/lessons/update/{lesson_id}: обновление несуществующего урока"""
        token = access_token_admin

        req_url = f"/api/v1/lessons/update/{uuid.uuid4()}"

        new_name = "Второй урок"
        update_payload = {"name": new_name}
        response = await aiohttp_client.put(
            req_url,
            json=update_payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Lesson not found"

    @pytest.mark.asyncio
    async def test_lesson_delete(
        self, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/lessons/{lesson_id}: удаление урока"""
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()
        await async_session.refresh(course)

        payload = {
            "name": "Первый урок",
            "desc": "Описание урока",
            "content": "Контент урока",
            "video_url": "http://example.com/jrn3o",
            "course_id": str(course.uuid),
        }
        lesson = Lesson(**payload)
        async_session.add(lesson)
        await async_session.commit()
        await async_session.refresh(lesson)

        token = access_token_admin

        req_url = f"/api/v1/lessons/{lesson.uuid}"
        response = await aiohttp_client.delete(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NO_CONTENT


    @pytest.mark.asyncio
    async def test_lesson_delete_error(
        self, aiohttp_client, async_session, access_token_admin
    ):
        """Тест /api/v1/lessons/{lesson_id}: удаление несуществующего урока"""
        token = access_token_admin

        req_url = f"/api/v1/lessons/{uuid.uuid4()}"
        response = await aiohttp_client.delete(
            req_url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Lesson not found"


    @pytest.mark.asyncio
    async def test_get_lesson_error(self, aiohttp_client, async_session, access_token):
        """Тест /api/v1/lessons/get/{lesson_id} с пустой таблицей уроков"""
        token = access_token
        req_url = f"/api/v1/lessons/get/{uuid.uuid4()}"

        response = await aiohttp_client.get(req_url, headers={"Authorization": f"Bearer {token['access_token']}"})

        assert response.status == HTTPStatus.NOT_FOUND
        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Lesson not found"

    @pytest.mark.asyncio
    async def test_get_lesson(self, aiohttp_client, async_session, access_token):
        """Тест /api/v1/lessons/get/{lesson_id}"""
        token = access_token
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()
        await async_session.refresh(course)

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

        req_url = f"/api/v1/lessons/get/{lesson.uuid}"

        response = await aiohttp_client.get(req_url, headers={"Authorization": f"Bearer {token['access_token']}"})

        assert response.status == HTTPStatus.OK
        if response.status == HTTPStatus.OK:
            content = await response.json()
            content["name"] = lesson.name


    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            ({"limit": 1, "skip": 1, "addon": 10}, {"status": HTTPStatus.OK, "len": 1}),
            ({"limit": 10, "skip": 4, "addon": 0}, {"status": HTTPStatus.OK, "len": 6}),
            (
                {"limit": 30, "skip": 40, "addon": 10},
                {"status": HTTPStatus.NOT_FOUND, "len": 1},
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_all_lesson(
        self, query_data, expected_data, aiohttp_client, async_session, access_token
    ):
        """
        Тест /api/v1/lessons/get_all/{course_id} с различными лимитами и количеством создаваемых данных в таблице уроков
        """
        token = access_token

        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()
        await async_session.refresh(course)


        for i in range(query_data["limit"] + query_data["addon"]):
            payload = {
                "name": f"Первый {i}",
                "desc": "Описание урока",
                "content": f"Контент урока {i}",
                "video_url": "http://example.com/jrn3o",
                "course_id": str(course.uuid),
            }
            lesson = Lesson(**payload)
            async_session.add(lesson)

        await async_session.commit()

        req_url = f"/api/v1/lessons/get_all/{course.uuid}/?limit={query_data['limit']}&skip={query_data['skip']}"
        response = await aiohttp_client.get(
            req_url, headers={"Authorization": f"Bearer {token['access_token']}"}
        )

        assert response.status == expected_data["status"]

        if response.status == expected_data["status"]:
            content = await response.json()

            assert len(content) == expected_data["len"]

    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            (
                {
                    "req_url": "/api/v1/lessons/create/",
                    "method": "post",
                    "payload": {
                        "name": "Пример",
                        "content": "string",
                        "course_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    },
                },
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "detail": f"Only admin can create lessons",
                },
            ),
            (
                {
                    "req_url": f"/api/v1/lessons/update/{uuid.uuid4()}",
                    "method": "put",
                    "payload": {},
                },
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "detail": f"Only admin can update lessons",
                },
            ),
            (
                {
                    "req_url": f"/api/v1/lessons/{uuid.uuid4()}",
                    "method": "delete",
                    "payload": {},
                },
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "detail": f"Only admin can delete lessons",
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_admin_user(
        self, query_data, expected_data, access_token, aiohttp_client, async_session
    ):
        """Тесты от пользователей не админов"""
        token = access_token

        if query_data["method"] == "post":
            response = await aiohttp_client.post(
                query_data["req_url"],
                json=query_data["payload"],
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
        elif query_data["method"] == "put":
            response = await aiohttp_client.put(
                query_data["req_url"],
                json=query_data["payload"],
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
        elif query_data["method"] == "delete":
            response = await aiohttp_client.delete(
                query_data["req_url"],
                json=query_data["payload"],
                headers={"Authorization": f"Bearer {token['access_token']}"},
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
                    "req_url": "/api/v1/lessons/create/",
                    "method": "post",
                },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
            (
                {
                    "req_url": f"/api/v1/lessons/update/{uuid.uuid4()}",
                    "method": "put",
                },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
            (
                {"req_url": f"/api/v1/lessons/{uuid.uuid4()}", "method": "delete"},
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
            (
                {
                    "req_url": f"/api/v1/lessons/get/{uuid.uuid4()}",
                    "method": "get",
                },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
            (
                {
                    "req_url": f"/api/v1/lessons/get_all/{uuid.uuid4()}",
                    "method": "get",
                },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_not_authorization(
        self, query_data, expected_data, aiohttp_client, async_session
    ):
        """Тесты без авторизации"""
        if query_data["method"] == "post":
            response = await aiohttp_client.post(
                query_data["req_url"], json={}
            )
        elif query_data["method"] == "put":
            response = await aiohttp_client.put(
                query_data["req_url"], json=expected_data
            )
        elif query_data["method"] == "delete":
            response = await aiohttp_client.delete(
                query_data["req_url"], json=expected_data
            )
        elif query_data["method"] == "get":
            response = await aiohttp_client.get(
                query_data["req_url"], json=expected_data
            )

        assert response.status == expected_data["status"]

        if response.status == expected_data["status"]:
            content = await response.json()
            assert content["detail"] == expected_data["detail"]

        await async_session.commit()