import uuid
import pytest

from http import HTTPStatus

from src.models.course import Course

class TestCourse:

    @pytest.mark.asyncio
    async def test_get_all_courses(self, aiohttp_client, async_session):
        """
        Тест /api/v1/courses/ с пустой таблицей курсов
        """
        req_url = "/api/v1/courses/"
        response = await aiohttp_client.get(req_url)
        assert response.status == HTTPStatus.NOT_FOUND
        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Courses not found"


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
    async def test_cat_all_param(
        self, query_data, expected_data, aiohttp_client, async_session
    ):
        """
        Тест /api/v1/courses/ с различными лимитами и количеством создаваемых данных в таблице курсов
        """
        req_url = (
            f"/api/v1/courses/?limit={query_data['limit']}&skip={query_data['skip']}"
        )

        for i in range(query_data["limit"] + query_data["addon"]):
            course = Course(name=f"Наименование курса-{i}", desc=f"Описание курса-{i}")
            async_session.add(course)

        await async_session.commit()
        response = await aiohttp_client.get(req_url)

        assert response.status == expected_data["status"]

        if response.status == expected_data["status"]:
            content = await response.json()

            assert len(content) == expected_data["len"]

    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            ({"addon": 0}, {"status": HTTPStatus.NOT_FOUND}),
            ({"addon": 10}, {"status": HTTPStatus.NOT_FOUND}),
        ],
    )
    @pytest.mark.asyncio
    async def test_courses_by_id_not_found(
        self, query_data, expected_data, aiohttp_client, async_session
    ):
        """
        Тесты /api/v1/courses/{course_id}: нет курса с искомым id
        """
        req_url = (
            f"/api/v1/courses/{uuid.uuid4()}"
        )

        for i in range(query_data["addon"]):
            course = Course(name=f"Наименование курса-{i}", desc=f"Описание курса-{i}")
            async_session.add(course)

        await async_session.commit()
        response = await aiohttp_client.get(req_url)

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Course not found"


    @pytest.mark.asyncio
    async def test_courses_by_id(self, aiohttp_client, async_session):
        """
        Тест //api/v1/courses/{course_id}: курс найден
        """
        name_course = "Наименование курса"
        course = Course(name=name_course, desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()
        await async_session.refresh(course)

        req_url = f"/api/v1/courses/{course.uuid}"
        response = await aiohttp_client.get(req_url)

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["name"] == name_course
