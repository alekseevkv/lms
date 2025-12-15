import uuid
import pytest

from http import HTTPStatus

from src.models.course import Course

class TestReviews:

    @pytest.mark.asyncio
    async def test_create_review(
        self, aiohttp_client, async_session, access_token
    ):
        """Тест /api/v1/reviews/: создание отзыва"""
        token = access_token
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()

        req_url = f"/api/v1/reviews/"

        payload = {
            "content": "Контент отзыва",
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
            assert content["course_id"] == str(course.uuid)

    @pytest.mark.asyncio
    async def test_create_review_error(
        self, aiohttp_client, access_token
    ):
        """Тест /api/v1/reviews/: создание отзыва к несуществующему курсу"""
        token = access_token
        req_url = f"/api/v1/reviews/"

        payload = {
            "content": "Контент отзыва",
            "course_id": str(uuid.uuid4()),
        }

        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Course not found"


    @pytest.mark.asyncio
    async def test_update_review(
        self, aiohttp_client, async_session, access_token
    ):
        """Тест /api/v1/reviews/{review_id}: обновление отзыва"""
        token = access_token
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()

        req_url = f"/api/v1/reviews/"

        payload = {
            "content": "Контент отзыва",
            "course_id": str(course.uuid),
        }

        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        review = await response.json()

        req_url = f"/api/v1/reviews/{review['uuid']}/"

        payload = {
            "content": "Обновленный отзыв",
        }

        response = await aiohttp_client.patch(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["content"] == "Обновленный отзыв"


    @pytest.mark.asyncio
    async def test_update_review_error(
        self, aiohttp_client, access_token
    ):
        """Тест /api/v1/reviews/{review_id}: обновление несуществующего отзыва"""
        token = access_token

        req_url = f"/api/v1/reviews/{uuid.uuid4()}/"

        payload = {
            "content": "Обновленный отзыв",
        }

        response = await aiohttp_client.patch(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.NOT_FOUND

        if response.status == HTTPStatus.NOT_FOUND:
            content = await response.json()
            assert content["detail"] == "Review not found"


    @pytest.mark.asyncio
    async def test_get_all_reviews(self, aiohttp_client, async_session, access_token):
        """
        Тест /api/v1/reviews/{course_id}: получение отзывов к курсу
        """
        token = access_token
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()

        req_url = f"/api/v1/reviews/"

        for i in range(5):
            payload = {
                "content": f"Контент отзыва {i}",
                "course_id": str(course.uuid),
            }

            await aiohttp_client.post(
                req_url,
                json=payload,
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )

        req_url = f"/api/v1/reviews/{str(course.uuid)}/"
        response = await aiohttp_client.get(req_url)

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert len(content) == 5


    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            (
                {
                    "req_url": "/api/v1/reviews/",
                    "method": "post",
                },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
            (
                {
                    "req_url": f"/api/v1/reviews/{uuid.uuid4()}/",
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
    async def test_not_authorization(
        self, query_data, expected_data, aiohttp_client, async_session
    ):
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

    @pytest.mark.asyncio
    async def test_get_all_reviews_whit_out_archived(self, aiohttp_client, async_session, access_token):
        """
        Тест /api/v1/reviews/{course_id}: получение отзывов к курсу (один отзыв удален)
        """
        token = access_token
        course = Course(name=f"Наименование курса", desc=f"Описание курса")
        async_session.add(course)
        await async_session.commit()

        req_url = f"/api/v1/reviews/"

        for i in range(5):
            payload = {
                "content": f"Контент отзыва {i}",
                "course_id": str(course.uuid),
            }

            res = await aiohttp_client.post(
                req_url,
                json=payload,
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )

        review = await res.json()
        req_url = f"/api/v1/reviews/{review['uuid']}?delete=true"

        await aiohttp_client.patch(
            req_url,
            json={},
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        req_url = f"/api/v1/reviews/{str(course.uuid)}/"
        response = await aiohttp_client.get(req_url)

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert len(content) == 4