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
        self, aiohttp_client, async_session, access_token
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

        assert response.status == HTTPStatus.CREATED

        if response.status == HTTPStatus.CREATED:
            content = await response.json()
            print("АААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААА")


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
        self, aiohttp_client, async_session, access_token
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

            response = await aiohttp_client.post(
                req_url,
                json=payload,
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
        review = await response.json()

        req_url = f"/api/v1/reviews/{str(course.uuid)}/"
        response = await aiohttp_client.get(req_url)

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert len(content) == 5